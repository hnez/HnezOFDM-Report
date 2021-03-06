DIAGRAM_FILES := $(wildcard ../../../diagrams/*.tex)
PREGEN_FILES := $(wildcard ../../../diagrams/*.pdf)

RENDER_FILES := $(subst ../../../diagrams/, , $(patsubst %.tex, %.render.tex, $(DIAGRAM_FILES)))

PDF_FILES := $(patsubst %.render.tex, %.pdf, $(RENDER_FILES))
SVG_FILES := $(patsubst %.pdf, %.svg, $(PDF_FILES))
SVG_FILES += $(subst ../../../diagrams/, , $(patsubst %.pdf, %.svg, $(PREGEN_FILES)))

LUALATEX= lualatex
LATEXRUN= ./latexrun
TEXINPUTS= .:..:../../../:

export TEXINPUTS

.PHONY: all
all: ${SVG_FILES}

%.render.tex: ../../../diagrams/%.tex
	$(file > $(@),\RequirePackage{luatex85})
	$(file >> $(@),\documentclass{standalone})
	$(file >> $(@),\usepackage{amsmath})
	$(file >> $(@),\usepackage{varwidth})
	$(file >> $(@),\usepackage{siunitx})
	$(file >> $(@),\DeclareSIUnit{\sample}{S})
	$(file >> $(@),\usepackage{verbatim})
	$(file >> $(@),\usepackage[usenames,dvipsnames]{xcolor})
	$(file >> $(@),\usepackage{bm})
	$(file >> $(@),\usepackage{tikz})
	$(file >> $(@),\usepackage{pgfplots})
	$(file >> $(@),\usepackage{circuitikz})
	$(file >> $(@),\usepackage{commath})
	$(file >> $(@),\usetikzlibrary{shapes,arrows,positioning,calc,fit,patterns,decorations.markings,matrix,3d})
	$(file >> $(@),\begin{document})
	$(file >> $(@), \input{$(<)})
	$(file >> $(@),\end{document})

%.pdf: %.render.tex
	${LATEXRUN} --latex-cmd ${LUALATEX} $(<) -o $(@)

%.svg: ../../../diagrams/%.pdf
	pdf2svg $(<) $(@)

%.svg: %.pdf
	pdf2svg $(<) $(@)
