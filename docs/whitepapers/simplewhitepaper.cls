\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{simplewhitepaper}[04/19/18 RIT Pushers LaTeX class]

\LoadClass[11pt]{article}

\RequirePackage[margin=1in]{geometry}
\RequirePackage{fancyhdr} %for footer
\RequirePackage{lastpage} %for footer page total count
\RequirePackage{vhistory} % For version history
\RequirePackage[hidelinks]{hyperref}
\RequirePackage{listings}
\RequirePackage{color}

\hypersetup{
	bookmarks=true,         % show bookmarks bar?
	pdfnewwindow=true,      % links in new PDF window
	colorlinks=true,        % false: boxed links; true: colored links
	linkcolor=black,        % color of internal links
	citecolor=black,        % color of links to bibliography
	filecolor=magenta,      % color of file links
	urlcolor=blue           % color of external links
}

%setup for listlisting colors and styles

\definecolor{lightgray}{rgb}{.9,.9,.9}
\definecolor{darkgray}{rgb}{.4,.4,.4}
\definecolor{purple}{rgb}{0.65, 0.12, 0.82}
\definecolor{mGreen}{rgb}{0,0.6,0}
\definecolor{mGray}{rgb}{0.5,0.5,0.5}
\definecolor{mPurple}{rgb}{0.58,0,0.82}
\definecolor{backgroundColour}{rgb}{0.95,0.95,0.92}

\lstdefinestyle{JavaScript}{
	keywords={typeof, new, true, false, catch, function, return, null, catch, switch, var, if, in, while, do, else, case, break},
	keywordstyle=\color{blue}\bfseries,
	ndkeywords={class, export, boolean, throw, implements, import, this},
	ndkeywordstyle=\color{darkgray}\bfseries,
	identifierstyle=\color{black},
	sensitive=false,
	comment=[l]{//},
	morecomment=[s]{/*}{*/},
	commentstyle=\color{purple}\ttfamily,
	stringstyle=\color{red}\ttfamily,
	morestring=[b]',
	numberstyle=\tiny\color{mGray},
	breakatwhitespace=false,
	breaklines=true,
	captionpos=b,
	keepspaces=true,
	numbers=left,
	numbersep=5pt,
	showspaces=false,
	showstringspaces=false,
	showtabs=false,
	tabsize=2,
	backgroundcolor=\color{backgroundColour},
	basicstyle=\footnotesize,
	morestring=[b]"
}

\lstdefinestyle{CStyle}{
	backgroundcolor=\color{backgroundColour},
	commentstyle=\color{mGreen},
	keywordstyle=\color{magenta},
	numberstyle=\tiny\color{mGray},
	stringstyle=\color{mPurple},
	basicstyle=\footnotesize,
	breakatwhitespace=false,
	breaklines=true,
	captionpos=b,
	keepspaces=true,
	numbers=left,
	numbersep=5pt,
	showspaces=false,
	showstringspaces=false,
	showtabs=false,
	tabsize=2,
	language=C
}

%uncomment if we dont want spaces between paragraphs
%\setlength{\parskip}{1ex} %--skip lines between paragraphs
%\setlength{\parindent}{0pt} %--don't indent paragraphs




% Define page style for title page (all minus the header)
\fancypagestyle{titlestyle}{%
	\fancyhf{}
	\fancyhead{}
	\lfoot{\footnotesize \documentdate}
	\rfoot{\footnotesize Page {\thepage} of \pageref{LastPage} }
	\cfoot{\footnotesize \documenttype}
	\setlength{\headheight}{14pt}
	\renewcommand{\headrulewidth}{0pt}
	\renewcommand{\footrulewidth}{0.4pt}
}

%main header/footer style
\fancypagestyle{documentstyle}{%
	\fancyhf{}
	\fancyhead{}
	\lhead{}
	\rhead{}
	\chead{\documenttitle}
	\lfoot{\footnotesize \documentdate}
	\rfoot{\footnotesize Page {\thepage} of \pageref{LastPage} }
	\cfoot{\footnotesize \documenttype}
	\setlength{\headheight}{14pt}
	\renewcommand{\headrulewidth}{0.4pt}
	\renewcommand{\footrulewidth}{0.4pt}
}

%define new titlepage style
\renewcommand{\maketitle}{
\pagestyle{titlestyle}

\begin{center}
	\vspace*{1cm}

	\Huge
	\textbf{\@title}

	\vspace{1.5cm}

	\LARGE
	\textbf{\@author}

	\vfill


\end{center}

\newpage
\pagestyle{documentstyle}
}

%change name of contents to table of contents when using \tableofcontents
% \renewcommand{\contentsname}{TABLE OF CONTENTS}
