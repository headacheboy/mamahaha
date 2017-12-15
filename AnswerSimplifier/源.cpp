#include <algorithm>
#include <iostream>
#include <fstream>
#include <sstream>
#include <codecvt>
#include <locale>
#include <string>
#include <vector>
#include <set>

using namespace std;

#define MAX_QUESTION 10000

//保留前多少个句子
#define KEEP_N	12

static vector<wstring> sens[MAX_QUESTION] = {};	//句子总集合
static vector<wstring> key[MAX_QUESTION];	//命名实体识别出来的单词

struct Node {
	wstring val, pos, rel;
	int parent, depth = -1;
};
static vector<Node> tree[MAX_QUESTION] = {};	//句法分析树，只对问题做了句法分析（段落的话太多，没有做）

static int questions = 0;

static void init(wifstream& f, string filename)
{
	f.open(filename);
	f.sync_with_stdio(false);
	f.imbue(locale(locale::empty(), new codecvt_utf8<wchar_t>));
}
static void init(wofstream& f, string filename)
{
	f.open(filename);
	f.sync_with_stdio(false);
	f.imbue(locale(locale::empty(), new codecvt_utf8<wchar_t>));
}
static int toint(const wstring& s)
{
	wstringstream ss(s);
	int a;
	ss >> a;
	return a;
}
static string ansfilename(int qnum)
{
	stringstream ss;
	ss << "ans\\ans" << qnum << ".txt";
	string fname;
	ss >> fname;
	return fname;
}

static void read_questions(const string& filename)
{
	cout << "Reading questions ... \n";

	wifstream inf;
	init(inf, filename);
	wofstream outf;
	init(outf, "tmp\\test0.txt");

	wstring s;
	questions = 0;
	while (inf) {
		getline(inf, s);
		if (s == L"")
			break;
		wstringstream ss(s);
		ss >> s;
		outf << s << endl;

		for (int i = 0; i < s.size(); i++) {
			wchar_t end = L'\0';

			switch (s[i]) {	//找特殊标点符号
			case L'“':
				end = L'”'; 
				break;
			case L'《':
				end = L'》';
				break;
			case L'"':
				end = L'"';
				break; 
			case L'『':
				end = L'』';
				break;
			}

			if (end != L'\0') {
				wstring t = L"";
				i++;
				while (i < s.size() && s[i] != end) {
					t += s[i];
					i++;
				}

				if (i != s.size() && t != L"")
					key[questions].push_back(t);	//用标点符号括起来的词一般是命名实体，把它加进去
			}
		}

		questions++;
	}
	inf.close();
	outf.close();
}

static void read_sens(const string& filename)	//读答案句子
{
	cout << "Reading sentences ... ";
	wifstream inf;
	init(inf, filename);

	int qnum = 0;
	wstring s, t;

	while (inf) {
		getline(inf, s);
		if (s == L"") {
			if ((qnum + 1) % 500 == 0)
				cout << " " << qnum + 1;

			qnum++;
			t = L"";
			continue;
		}

		for (int j = 0; j < s.length(); j++) {
			if (s[j] == L'。') {
				//if (t != L"")
					sens[qnum].push_back(t + s[j]);
				t = L"";
			}
			else if (s[j] != L' ')
				t += s[j];
		}
		if (t != L"")
			sens[qnum].push_back(t);
	}
	cout << endl;

	inf.close();
}

static void read_parse()	//读句法分析结果
{
	wifstream inf;
	init(inf, "tmp\\parse.txt");

	int qnum = 0;
	while (inf) {
		wstring s;
		for (int i = 0; i < 6; i++)
			getline(inf, s);

		while (inf) {
			getline(inf, s);
			if (s == L"            </sent>")
				break;

			int count = 0;
			wstring t = L"";
			Node x;
			for (int i = 0; i < s.length(); i++) {
				if (s[i] == L'"' || s[i] == L'\'') {
					count++;

					switch (count) {
					case 4:
						x.val = t; break;
					case 6:
						x.pos = t; break;
					case 8:
						x.parent = toint(t); break;
					case 10:
						x.rel = t;
						tree[qnum].push_back(x);
					}

					t = L"";
				}
				else
					t += s[i];
			}
		}

		qnum++;

		getline(inf, s);
		while (inf && s != L"")
			getline(inf, s);
	}
}

static void read_ner()	//读命名实体识别结果
{
	wifstream inf;
	init(inf, "tmp\\ner.txt");

	int qnum = 0;
	while (inf) {
		wstring s;
		getline(inf, s);

		wstringstream ss(s);
		wstring t = L"", lastt = L"", lastatt = L"", att = L"";
		while (ss >> t) {
			auto p = t.find(L'N');
			if (p != wstring::npos) {
				att = t[p] + t[p + 1];
				if (att != lastatt) {
					if (lastt != L"")
						key[qnum].push_back(lastt);
					lastt = L"";
					lastatt = att;
				}
				lastt += t.substr(0, t.find(L'/'));
			}
			else
				lastatt = L"";
		}
		if (lastt != L"")
			key[qnum].push_back(lastt);

		qnum++;
	}
}

static int find_depth(int qnum, int i)	//获得分析树深度
{
	if (tree[qnum][i].parent == -1)
		return tree[qnum][i].depth = 0;
	int t = tree[qnum][tree[qnum][i].parent].depth;
	return (t != -1) ? t :
		tree[qnum][i].depth = find_depth(qnum, tree[qnum][i].parent) + 1;
}

static void do_ltp()	//调用ltp库
{
	cout << "Using ltp library ... \n";
	system("ltp\\cws_cmdline.exe --threads 4 --segmentor-model ltp\\ltp_data\\cws.model --input tmp\\test0.txt > tmp\\test1.txt");
	system("ltp\\pos_cmdline.exe --threads 4 --postagger-model ltp\\ltp_data\\pos.model --input tmp\\test1.txt > tmp\\test2.txt");
	//system("ltp\\par_cmdline.exe --threads 2 --parser-model ltp\\ltp_data\\parser.model --input test2.txt > test3.txt");
	system("ltp\\ner_cmdline.exe --threads 4 --ner-model ltp\\ltp_data\\ner.model --input tmp\\test2.txt > tmp\\ner.txt");
	system("ltp\\ltp_test.exe --threads 4 --last-stage dp "
		"--segmentor-model ltp\\ltp_data\\cws.model "
		"--postagger-model ltp\\ltp_data\\pos.model "
		"--parser-model ltp\\ltp_data\\parser.model "
		//"--ner-model ltp\\ltp_data\\ner.model "
		"--input tmp\\test0.txt > tmp\\parse.txt");
}

struct comp_s {
	double score;
	int i;
};
static bool comp(comp_s a, comp_s b) {
	return a.score > b.score;
}

static void select_sens(wofstream& outf, int qnum)	//评分、排序
{
	int sens_n = sens[qnum].size();
	int tree_n = tree[qnum].size();

	vector<comp_s> c;
	c.resize(sens_n);
	for (int i = 0; i < sens_n; i++)
		c[i].i = i;

	for (int i = 0; i < tree_n; i++) {	//遍历每个词
		find_depth(qnum, i);

		if (tree[qnum][i].pos == L"u" ||	//去掉助词
			tree[qnum][i].pos == L"wp" ||	//去掉标点
			tree[qnum][i].val == L"是")
			continue;

		if (tree[qnum][i].pos == L"r") {	//去掉疑问代词
			if (tree[qnum][i].val.size() == 1) {
				while (tree[qnum][i].parent == i + 1)
					i++;
			}
			continue;
		}

		vector<int> exist;
		for (int j = 0; j < sens_n; j++) {
			if (sens[qnum][j].find(tree[qnum][i].val) != wstring::npos) {
				exist.push_back(j);
			}
		}

		double idf = exist.size() != 0 ? log(sens_n / exist.size()) : 0;
		for (int x : exist) {
			c[x].score += idf * (10 - tree[qnum][i].depth);	//根据idf和分析树深度打分
		}
	}

	for (wstring keyword : key[qnum]) {
		vector<int> exist;
		for (int i = 0; i < sens_n; i++) {
			if (sens[qnum][i].find(keyword) != wstring::npos) {
				exist.push_back(i);
			}
		}

		double idf = exist.size() != 0 ? log(sens_n / exist.size()) : 0;
		for (int x : exist) {
			if (x > 0)
				c[x - 1].score += idf * 3;
			c[x].score += idf * 10;	//出现命名实体的有加分
			if (x < sens_n - 1)
				c[x + 1].score += idf * 3;	//出现在上下文也加点分
		}
	}

	sort(c.begin(), c.end(), comp);

	outf << qnum << endl;
	for (int i = 0; i < min<int>(KEEP_N, sens_n); i++) {
		int x = c[i].i;
		if (x > 0)
			if (sens[qnum][x - 1] != L"。")
				outf << sens[qnum][x - 1];
		if (sens[qnum][x] != L"。")
			outf << sens[qnum][x];
		outf << endl;
	}
	outf << endl << endl;
}

static void do_select(const string& filename)
{
	cout << "Selecting ... ";
	wofstream outf;
	init(outf, filename);

	//questions = 8000;
	for (int i = 0; i < questions; i++) {
		if ((i + 1) % 500 == 0)
			cout << " " << i + 1;
		select_sens(outf, i);
	}
	cout << endl;
	outf.close();
}

int main()
{
	read_questions("input");

	do_ltp();
	read_parse();
	read_ner();

	read_sens("output");
	do_select("ans.txt");
	
	system("pause");
}