.PHONY: all build clean_aux clean help
.SILENT: clean_aux example.pdf gdbgui.pdf clean help

documents = args.pdf

all: build
	
#pattern matching to build all documents
$(documents): %.pdf: %.tex
	echo Building $@ ...
	pdflatex $(basename $@)
	#running second time as required by lastpage
	pdflatex $(basename $@)

build: $(documents) clean_aux

clean_aux:
	echo Cleaning up all auxilary files...
	-rm -rf *.log *.aux *.dvi *.lof *.lot *.bit *.idx *.glo *.bbl *.bcf *.ilg *.toc *.ind *.out *.blg *.fdb_latexmk *.fls *synctex.gz *.ver *.hst

clean: clean_aux
	echo Cleaning all pdfs
	-rm -rf *.pdf

help:
	echo "Make options: all, clean, clean_aux, help"

