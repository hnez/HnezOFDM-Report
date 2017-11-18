THEME_DIR= ../theme/boring
SLIDE_COMPILER= landslide
NOTES_COMPILER= pandoc

NOTES= final-notes.html intermediate-notes.html
SLIDES= final.html intermediate.html

.PHONY: all
all: $(NOTES) $(SLIDES)

%.html: ../src/%.md
	cp $(<) tmp.md
	$(SLIDE_COMPILER) -c -d $(@) -r -t $(THEME_DIR) tmp.md
	rm tmp.md

%-notes.html: ../notes/%.md style.html.inc
	$(NOTES_COMPILER) -o $@ $< -H style.html.inc

.PHONY: public
public: all
	rsync -av . tut@zerforscht.de:public_html/bap
