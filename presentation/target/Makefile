THEME_DIR= ../theme/boring
SLIDE_COMPILER= landslide
NOTES_COMPILER= pandoc

.PHONY: all
all: presentation.html notes.html

presentation.html: ../src/presentation.md
	cp $(<) sofi.md
	$(SLIDE_COMPILER) -c -d $(@) -r -t $(THEME_DIR) sofi.md
	rm sofi.md

notes.html: ../src/notes.md style.html.inc
	$(NOTES_COMPILER) -o $@ $< -H style.html.inc

.PHONY: public
public: all
	rsync -av . tut@zerforscht.de:public_html/bap
