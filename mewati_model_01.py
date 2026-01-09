# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, ttk
from nltk import Tree
from nltk.draw.util import CanvasFrame
from nltk.draw import TreeWidget
import re

# -------- Helpers --------
def normalize_sentence(s: str) -> str:
    if not s:
        return ""
    s = s.replace("۔", "").replace("؟", "").replace("!", "").strip()
    s = re.sub(r"\s+", " ", s)
    return s

def show_table_popup(root, title: str, headers, rows, special_header_index=None):
    """Compact popup table: thin borders, selectable, full-table copyable (with headers)."""
    import tkinter as tk
    from tkinter import ttk

    # --- Popup setup ---
    top = tk.Toplevel(root)
    top.title(title)
    top.geometry("480x240")  # Compact, Word-page size

    frame = tk.Frame(top, bg="white", bd=1, relief="solid")
    frame.pack(fill="both", expand=True, padx=3, pady=3)

    # --- Style setup ---
    style = ttk.Style()
    style.theme_use("default")
    style.configure(
        "Treeview",
        background="white",
        foreground="black",
        rowheight=18,
        fieldbackground="white",
        borderwidth=0,
        font=("Times New Roman", 10)
    )
    style.configure("Treeview.Heading", font=("Times New Roman", 10, "bold"), relief="flat")
    style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])  # Removes thick frame

    # --- Treeview setup ---
    tree = ttk.Treeview(frame, columns=headers, show="headings", selectmode="extended")

    for col in headers:
        tree.heading(col, text=col, anchor="w")
        max_width = max([len(str(r[headers.index(col)])) for r in rows] + [len(col)]) * 7
        tree.column(col, width=max_width, anchor="w", stretch=False)

    # Insert data rows
    for idx, row in enumerate(rows):
        if special_header_index is not None and idx == special_header_index:
            tree.insert("", "end", values=row, tags=("headerrow",))
        else:
            tree.insert("", "end", values=row)
    tree.tag_configure("headerrow", font=("Times New Roman", 10, "bold"))

    tree.pack(fill="both", expand=True, padx=1, pady=1)

    # --- Select All (Ctrl + A) ---
    def select_all(event=None):
        tree.selection_set(tree.get_children())
        return "break"

    top.bind("<Control-a>", select_all)

    # --- Copy (Ctrl + C): copies selected rows with headers ---
    def copy_selected(event=None):
        selected = tree.selection()

        # Always start with headers
        lines = ["\t".join(headers)]

        if selected:
            # Add only selected rows
            for item in selected:
                values = [str(v) for v in tree.item(item)["values"]]
                lines.append("\t".join(values))
        else:
            # Add all rows if none selected
            for r in rows:
                lines.append("\t".join(map(str, r)))

        content = "\n".join(lines)
        top.clipboard_clear()
        top.clipboard_append(content)
        top.update()
        return "break"

    top.bind("<Control-c>", copy_selected)

    # --- Thin border simulation ---
    def draw_thin_lines(event=None):
        for item in tree.get_children():
            tree.item(item, tags=("thinborder",))
        tree.tag_configure("thinborder", background="white")

    tree.bind("<Expose>", draw_thin_lines)


# -------- Morphological Features --------
MORPH_FEATURES = {
    "جب ہماری کلاس لگے کرے ای": [
        ("جب", "جب", "Subordinating Conjunction (Temporal)", "—", "Introduces time clauses."),
        ("ہماری کلاس", "ہماری کلاس", "[ہم + اری] = Possessive Pronoun + Noun", "اری → ہماری", "Dialectal form of 'ہماری'."),
        ("لگے", "لگتی", "[لگ + ے + کرے] = Root Verb + Aspect + Aux", "لگے کرے → لگتی", "Compound with habitual aspect."),
        ("کرے ای", "تھی", "Copula/Aspect Marker (3rd fem past)", "ای → تھی", "Reduced form of 'تھی'."),
    ],
    "کہ او کتنو پختو لکھاری اے": [
        ("کہ", "کہ", "Subordinating Conjunction", "—", "Same as Urdu."),
        ("او", "وہ", "3rd Person Pronoun", "او → وہ", "Dialectal variation."),
        ("کتنو پختو", "کتنا اچھا", "Interrogative + Adjective", "→ کتنا اچھا", "Equivalent phrase."),
        ("لکھاری", "لکھاری", "Agent noun", "—", "Same as Urdu."),
        ("اے", "ہے", "Copula", "اے → ہے", "Dialectal copula."),
    ],
    "اگر وے یا لباس اے پہری راکھاں": [
        ("اگر", "اگر", "Conditional Conjunction", "—", "Identical."),
        ("وے", "وہ", "Pronoun", "وے → وہ", "Mewati form."),
        ("یا", "یہ/اس", "Demonstrative", "→ یہ/اس", "Dialectal."),
        ("لباس اے", "لباس کو", "[Noun + Postposition]", "اے → کو", "Case marking difference."),
        ("پہری راکھاں", "پہنتے ہیں", "Verb compound", "→ پہنتے ہیں", "Aspectual equivalence."),
    ],
    "گیانی اور تعلیم کا ماہر لوگن کو ای ماننواے": [
        ("گیانی", "دانشور", "Noun", "—", "Borrowed word."),
        ("اور", "اور", "Conjunction", "—", "Same."),
        ("تعلیم کا ماہر", "تعلیم کے ماہر", "NP + Genitive", "کا → کے", "Case shift."),
        ("لوگن کو", "لوگوں کو", "Plural Oblique + Dative", "ن → وں", "Plural form."),
        ("ای", "یہ", "Demonstrative", "ای → یہ", "Variant."),
        ("ماننواے", "ماننا ہے", "Root + Inf + Aux", "→ ماننا ہے", "Fusion."),
    ],
    "میرے مارے بی اب تک ایک اچھنبو سوای اے": [
        ("میرے مارے", "میرے لیے", "Possessive + Postposition", "مارے → لیے", "Dialectal."),
        ("بی", "بھی", "Particle", "→ بھی", "Colloquial."),
        ("اب تک", "اب تک", "Temporal", "—", "Same."),
        ("ایک", "ایک", "Numeral", "—", "Identical."),
        ("اچھنبو سوای", "حیرانگی سی", "Adj + Postposition", "→ حیرانگی سی", "Lexical difference."),
        ("اے", "ہے", "Copula", "→ ہے", "Variant."),
    ],
    "دنیا آ جا ری ہی": [
        ("دنیا", "دنیا", "Noun", "—", "Same."),
        ("آ", "آ", "Aspectual Prefix", "—", "Identical."),
        ("جا ری", "جا رہی", "Verb Compound", "ری → رہی", "Phonemic reduction."),
        ("ہی", "ہے", "Copula", "ہی → ہے", "Variant."),
    ],
    "کا ہم ماضی اے زندہ رکھ سکاں": [
        ("کا", "کیا", "Question particle", "→ کیا", "Interrogative."),
        ("ہم", "ہم", "1PL Pronoun", "—", "Same."),
        ("ماضی اے", "ماضی کو", "Noun + Dative", "اے → کو", "Postpositional variant."),
        ("زندہ", "زندہ", "Adjective", "—", "Same."),
        ("رکھ", "رکھ", "Verb Root", "—", "Same."),
        ("سکاں", "سکتے ہیں", "Modal Auxiliary", "→ سکتے ہیں", "Plural auxiliary."),
    ],
    "کہا میو روس میں باولا ہو گا": [
        ("کہا", "کیا", "Interrogative", "→ کیا", "Variant."),
        ("میو", "میو", "Ethnonym", "—", "Same."),
        ("روس میں", "روس میں", "Noun + Locative", "—", "Same."),
        ("باولا", "پاگل", "Adjective", "→ پاگل", "Equivalent meaning."),
        ("ہو گا", "ہو گیا", "Auxiliary", "→ ہو گیا", "Tense/aspect difference."),
    ],
    "کہا پوچھو جائیگو قبر میں": [
        ("کہا", "کیا", "Interrogative", "→ کیا", "Variant."),
        ("پوچھو", "پوچھا", "Verb root", "→ پوچھا", "Dialectal form."),
        ("جائیگو", "جائے گا", "Passive Future", "→ جائے گا", "Future passive."),
        ("قبر میں", "قبر میں", "Noun + Locative", "—", "Same."),
    ],
    "اوکہن جا رو اے": [
        ("او", "وہ", "Pronoun", "او → وہ", "Variant."),
        ("کہن", "کہاں", "Interrogative Adverb", "کہن → کہاں", "Dialectal shift."),
        ("جا رو", "جا رہا", "Verb compound", "رو → رہا", "Progressive."),
        ("اے", "ہے", "Copula", "→ ہے", "Variant."),
    ],
    "تینے کہا کھایو": [
        ("تینے", "تم نے", "2SG + ERG", "→ تم نے", "Case marking."),
        ("کہا", "کیا", "Interrogative", "→ کیا", "Variant."),
        ("کھایو", "کھایا", "Verb (perfective)", "یو → یا", "Perfective change."),
    ],
    "ہم رات کب سویا ہا": [
        ("ہم", "ہم", "Pronoun", "—", "Same."),
        ("رات", "رات", "Noun", "—", "Same."),
        ("کب", "کب", "Interrogative", "—", "Same."),
        ("سویا ہا", "سوئے تھے", "Verb + Aux", "ہا → تھے", "Aux difference."),
    ],
    "ای جاڑان کی بات ای": [
        ("ای", "یہ", "Demonstrative", "→ یہ", "Variant."),
        ("جاڑان کی", "جاڑوں کی", "Noun + Genitive", "ان → وں", "Plural suffix."),
        ("بات", "بات", "Noun", "—", "Same."),
        ("ای", "ہے", "Copula", "→ ہے", "Variant."),
    ],
    "او اچھو آدمی ہو": [
        ("او", "وہ", "Pronoun", "او → وہ", "Dialectal."),
        ("اچھو", "اچھا", "Adjective", "او → اا", "Phonological."),
        ("آدمی", "آدمی", "Noun", "—", "Same."),
        ("ہو", "تھا", "Copula", "→ تھا", "Tense difference."),
    ],
    "بیربانی بڑی ملوک ہی": [
        ("بیربانی", "عورت", "Noun", "→ عورت", "Different lexeme."),
        ("بڑی", "بہت", "Adverb", "→ بہت", "Intensifier shift."),
        ("ملوک", "خوبصورت", "Adjective", "→ خوبصورت", "Semantic equivalent."),
        ("ہی", "تھی", "Copula", "→ تھی", "Past tense copula."),
    ],
    "بوڑھی اماں نے کدی کائی کی برائی نہ کری": [
        ("بوڑھی", "بوڑھی", "Adjective", "—", "Same."),
        ("اماں", "ماں", "Noun", "→ ماں", "Dialectal variant."),
        ("نے", "نے", "Ergative", "—", "Same."),
        ("کدی", "کبھی", "Adverb", "→ کبھی", "Variant."),
        ("کائی کی", "کسی کی", "Pronoun + Poss", "→ کسی کی", "Lexical."),
        ("برائی", "برائی", "Noun", "—", "Same."),
        ("نہ کری", "نہیں کی", "Neg + Verb", "→ نہیں کی", "Negation."),
    ],
    "میواتی زبان اپنی بقا کی جنگ لڑری اے": [
        ("میواتی زبان", "میواتی زبان", "Proper noun phrase", "—", "Same."),
        ("اپنی", "اپنی", "Possessive pronoun", "—", "Same."),
        ("بقا کی جنگ", "بقا کی جنگ", "NP + Genitive", "—", "Same."),
        ("لڑری", "لڑ رہی", "Verb Progressive", "ری → رہی", "Phonemic."),
        ("اے", "ہے", "Copula", "→ ہے", "Variant."),
    ],
    "بزرگن کی بہت سی سنت ٹوٹتی دکھائی دے ری ہاں": [
        ("بزرگن کی", "بزرگوں کی", "Plural + Gen", "ن → وں", "Plural ending."),
        ("بہت سی", "بہت سی", "Quantifier", "—", "Same."),
        ("سنت", "سنت", "Noun", "—", "Same."),
        ("ٹوٹتی", "ٹوٹتی", "Verb progressive", "—", "Same."),
        ("دکھائی دے", "دکھائی دے", "Light verb", "—", "Same."),
        ("ری ہاں", "رہی ہیں", "Progressive + Copula", "ری ہاں → رہی ہیں", "Dialectal plural."),
    ],
    "گول مٹول سلونٹن سو بھر و چہرو": [
        ("گول مٹول", "گول مٹول", "Adjective", "—", "Same."),
        ("سلونٹن", "جھریاں", "Noun", "→ جھریاں", "Lexical substitution."),
        ("سو", "سے", "Postposition", "→ سے", "Case marker."),
        ("بھر و", "بھرا", "Verb participle", "→ بھرا", "Aspect."),
        ("چہرو", "چہرہ", "Noun", "→ چہرہ", "Dialectal."),
    ],
    "کپڑا کی لوگڑی": [
        ("کپڑا", "کپڑا", "Noun", "—", "Same."),
        ("کی", "کا", "Genitive", "کی → کا", "Gender shift."),
        ("لوگڑی", "دوپٹہ", "Noun", "→ دوپٹہ", "Lexical."),
    ],
    "یا کا منہ سو": [
        ("یا", "یہ", "Demonstrative", "→ یہ", "Dialectal."),
        ("کا", "کا", "Genitive", "—", "Same."),
        ("منہ سو", "منہ سے", "Noun + Postposition", "سو → سے", "Postposition."),
    ],
}

# -------- SpaCy Features --------
SPACY_FEATURES = {
    "جب ہماری کلاس لگے کرے ای": [
        ["جب", "جب", "SCONJ", "mark", "Subordinating Conjunction (Temporal)", "کرے"],
        ["ہماری", "ہم", "PRON", "nmod:poss", "Possessive Pronoun", "کلاس"],
        ["کلاس", "کلاس", "NOUN", "nsubj", "Noun (subject of verb)", "کرے"],
        ["لگے", "لگنا", "VERB", "aux", "Root Verb + Aspect + Aux", "کرے"],
        ["کرے", "کرنا", "AUX", "root", "Habitual auxiliary verb", "—"],
        ["ای", "ہونا", "AUX", "cop", "Reduced Copula form of تھی", "—"]
    ],
    "کہ او کتنو پختو لکھاری اے": [
        ["کہ", "کہ", "SCONJ", "mark", "Subordinating Conjunction", "لکھاری"],
        ["او", "وہ", "PRON", "nsubj", "3rd Person Pronoun", "لکھاری"],
        ["کتنو", "کتنا", "ADJ", "amod", "Interrogative adjective", "پختو"],
        ["پختو", "اچھا", "ADJ", "amod", "Quality adjective", "لکھاری"],
        ["لکھاری", "لکھاری", "NOUN", "root", "Agent noun", "—"],
        ["اے", "ہے", "AUX", "cop", "Copula (3rd person singular)", "لکھاری"]
    ],
    "اگر وے یا لباس اے پہری راکھاں": [
        ["اگر", "اگر", "SCONJ", "mark", "Conditional conjunction", "راکھاں"],
        ["وے", "وہ", "PRON", "nsubj", "3rd Person Pronoun", "راکھاں"],
        ["یا", "یہ", "PRON", "det", "Demonstrative pronoun", "لباس"],
        ["لباس", "لباس", "NOUN", "obj", "Noun", "راکھاں"],
        ["اے", "کو", "ADP", "case", "Postposition marker", "لباس"],
        ["پہری", "پہننا", "VERB", "aux", "Root verb + aspect", "راکھاں"],
        ["راکھاں", "رکھنا", "AUX", "root", "Light verb + copula", "—"]
    ],
    "گیانی اور تعلیم کا ماہر لوگن کو ای ماننواے": [
        ["گیانی", "دانشور", "NOUN", "compound", "Noun (agent)", "ماہر"],
        ["اور", "اور", "CCONJ", "cc", "Coordinating conjunction", "گیانی"],
        ["تعلیم", "تعلیم", "NOUN", "compound", "Part of NP", "ماہر"],
        ["کا", "کا", "ADP", "case", "Genitive postposition", "تعلیم"],
        ["ماہر", "ماہر", "NOUN", "nsubj", "Expert noun", "ماننواے"],
        ["لوگن", "لوگ", "NOUN", "nmod", "Plural oblique", "ماننواے"],
        ["کو", "کا", "ADP", "case", "Postposition", "لوگن"],
        ["ای", "یہ", "PRON", "nsubj", "Demonstrative pronoun", "ماننواے"],
        ["ماننواے", "ماننا ہے", "VERB", "root", "Infinitive + Aux", "—"],
        ["اے", "ہے", "AUX", "cop", "Copula", "ماننواے"]
    ],
    "میرے مارے بی اب تک ایک اچھنبو سوای اے": [
        ["میرے", "میرا", "PRON", "nmod:poss", "Possessive pronoun", "مارے"],
        ["مارے", "لیے", "ADP", "case", "Postposition", "میرے"],
        ["بی", "بھی", "PART", "advmod", "Focus/emphasis particle", "اے"],
        ["اب تک", "اب تک", "ADV", "advmod", "Temporal phrase", "اے"],
        ["ایک", "ایک", "NUM", "nummod", "Cardinal numeral", "سوای"],
        ["اچھنبو", "عجیب", "ADJ", "amod", "Adjective", "سوای"],
        ["سوای", "سی", "ADP", "obl", "Postposition", "اے"],
        ["اے", "ہے", "AUX", "root", "Copula (present tense)", "—"]
    ],
    "دنیا آ جا ری ہی": [
        ["دنیا", "دنیا", "NOUN", "nsubj", "Noun (subject)", "جاری"],
        ["آ", "آنا", "PART", "aux", "Aspectual prefix", "جاری"],
        ["جاری", "جا رہی", "VERB", "root", "Verb + progressive", "—"],
        ["ہی", "ہے", "AUX", "cop", "Copula", "جاری"]
    ],
    "کا ہم ماضی اے زندہ رکھ سکاں": [
        ["کا", "کیا", "PART", "aux", "Interrogative particle", "سکاں"],
        ["ہم", "ہم", "PRON", "nsubj", "1PL pronoun", "سکاں"],
        ["ماضی", "ماضی", "NOUN", "obj", "Noun (indirect object)", "رکھ"],
        ["اے", "کو", "ADP", "case", "Postposition", "ماضی"],
        ["زندہ", "زندہ", "ADJ", "amod", "Adjective (state)", "رکھ"],
        ["زندہ رکھ", "زندہ رکھ", "VERB", "xcomp", "Compound verb", "سکاں"],
        ["رکھ", "رکھتے", "VERB", "compound", "Root verb", "سکاں"],
        ["سکاں", "سکتے ہیں", "AUX", "root", "Modal auxiliary", "—"]
    ],
    "کہا میو روس میں باولا ہو گا": [
        ["کہا", "کیا", "PART", "aux", "Interrogative particle", "باولا"],
        ["میو", "میو", "NOUN", "nsubj", "Ethnonym/proper noun", "باولا"],
        ["روس میں", "روس میں", "PROPN", "obl", "Proper noun locative", "باولا"],
        ["باولا", "پاگل", "ADJ", "amod", "Adjective", "میو"],
        ["ہو گا", "ہو گیا", "AUX", "root", "Auxiliary tense/aspect", "—"]
    ],
    "کہا پوچھو جائیگو قبر میں": [
        ["کہا", "کیا", "PART", "aux", "Interrogative particle", "پوچھو"],
        ["پوچھو", "پوچھا", "VERB", "root", "Imperative verb", "—"],
        ["جائیگو", "جائے گا", "VERB", "conj", "Future passive verb phrase", "پوچھو"],
        ["قبر میں", "قبر میں", "NOUN", "obl", "Locative noun", "جائیگو"]
    ],
    "اوکہن جا رو اے": [
        ["او", "وہ", "PRON", "nsubj", "3rd person pronoun", "جا رو"],
        ["کہن", "کہاں", "ADV", "advmod", "Interrogative locative", "جا رو"],
        ["جا رو", "جا رہا", "VERB", "root", "Verb compound: progressive", "—"],
        ["اے", "ہے", "AUX", "aux", "Copula", "جا رو"]
    ],
    "تینے کہا کھایو": [
        ["تینے", "تم نے", "PRON", "nsubj", "2SG pronoun + ergative", "کھایو"],
        ["کہا", "کیا", "INTJ", "obj", "Interrogative pronoun", "کھایو"],
        ["کھایو", "کھایا", "VERB", "root", "Perfective verb", "—"]
    ],
    "ہم رات کب سویا ہا": [
        ["ہم", "ہم", "PRON", "nsubj", "1PL pronoun", "سویا ہا"],
        ["رات", "رات", "NOUN", "nmod", "Temporal noun", "سویا ہا"],
        ["کب", "کب", "ADV", "advmod", "Interrogative adverb", "سویا ہا"],
        ["سویا ہا", "سوئے تھے", "VERB", "root", "Compound verb (past perfective)", "—"]
    ],
    "ای جاڑان کی بات ای": [
        ["ای", "یہ", "PRON", "nsubj", "Demonstrative pronoun", "بات"],
        ["جاڑان کی", "جاڑوں کی", "NOUN", "nmod", "Plural/Genitive noun", "بات"],
        ["بات", "بات", "NOUN", "root", "Common noun", "—"],
        ["ای", "ہے", "AUX", "cop", "Copula", "بات"]
    ],
    "او اچھو آدمی ہو": [
        ["او", "وہ", "PRON", "nsubj", "3rd person pronoun", "آدمی"],
        ["اچھو", "اچھا", "ADJ", "amod", "Adjective", "آدمی"],
        ["آدمی", "آدمی", "NOUN", "root", "Common noun", "—"],
        ["ہو", "تھا", "AUX", "cop", "Past copula", "آدمی"]
    ],
    "بیربانی بڑی ملوک ہی": [
        ["بیربانی", "عورت", "NOUN", "nsubj", "Noun (feminine)", "ملوک"],
        ["بڑی", "بہت", "ADV", "advmod", "Intensifier/adverb", "ملوک"],
        ["ملوک", "خوبصورت", "ADJ", "amod", "Adjective", "بیربانی"],
        ["ہی", "تھی", "AUX", "cop", "Past copula", "ملوک"]
    ],
    "بوڑھی اماں نے کدی کائی کی برائی نہ کری": [
        ["بوڑھی", "بوڑھی", "ADJ", "amod", "Adjective", "اماں"],
        ["اماں", "ماں", "NOUN", "nsubj", "Kinship noun", "کری"],
        ["نے", "نے", "ADP", "case", "Ergative marker", "اماں"],
        ["کدی", "کبھی", "ADV", "advmod", "Temporal adverb", "کری"],
        ["کائی کی", "کسی کی", "PRON", "nmod:poss", "Possessive pronoun", "برائی"],
        ["برائی", "برائی", "NOUN", "obj", "Abstract noun", "کری"],
        ["نہ کری", "نہیں کی", "VERB", "ROOT", "Neg + Verb", "—"]
    ],
    "میواتی زبان اپنی بقا کی جنگ لڑری اے": [
        ["میواتی زبان", "میواتی زبان", "PROPN", "compound", "Proper noun", "زبان"],
        ["اپنی", "اپنی", "PRON", "poss", "Reflexive possessive", "بقا"],
        ["بقا کی جنگ", "بقا کی جنگ", "NOUN", "nmod", "Abstract noun", "لڑری"],
        ["لڑری", "لڑ رہی", "VERB", "root", "Verb + progressive participle", "—"],
        ["اے", "ہے", "AUX", "cop", "Copula", "لڑری"]
    ],
    "بزرگن کی بہت سی سنت ٹوٹتی دکھائی دے ری ہاں": [
        ["بزرگن کی", "بزرگوں کی", "NOUN", "nmod", "Plural + Genitive", "سنت"],
        ["بہت سی", "بہت سی", "ADJ", "amod", "Quantifier", "سنت"],
        ["سنت", "سنت", "NOUN", "nsubj", "Noun", "ٹوٹتی"],
        ["ٹوٹتی", "ٹوٹتی", "VERB", "acl", "Verb progressive", "سنت"],
        ["دکھائی دے", "دکھائی دے", "VERB", "xcomp", "Light verb", "ٹوٹتی"],
        ["ری ہاں", "رہی ہیں", "AUX", "aux", "Progressive + Copula", "دکھائی دے"]
    ],
    "گول مٹول سلونٹن سو بھر و چہرو": [
        ["گول مٹول", "گول مٹول", "ADJ", "amod", "Adjective", "چہرو"],
        ["سلونٹن", "جھریاں", "NOUN", "amod", "Lexical substitution", "چہرو"],
        ["سو بھر", "بھرا", "VERB", "amod", "Perfective participle", "چہرو"],
        ["و", "ہوا", "AUX", "aux", "Aux/Copula", "سو بھر"],
        ["چہرو", "چہرہ", "NOUN", "root", "Head noun", "—"]
    ],
    "کپڑا کی لوگڑی": [
        ["کپڑا", "کپڑا", "NOUN", "nmod", "Noun", "لوگڑی"],
        ["کی", "کا", "ADP", "case", "Genitive postposition", "کپڑا"],
        ["لوگڑی", "دوپٹہ", "NOUN", "root", "Regional equivalent", "—"]
    ],
    "یا کا منہ سو": [
        ["یا", "یہ", "PRON", "nmod", "Demonstrative pronoun", "منہ"],
        ["کا", "کا", "ADP", "case", "Possessive postposition", "یا"],
        ["منہ سو", "منہ سے", "NOUN", "obl", "Noun + Postposition", "سو"]
    ]
}

# -------- Leipzig Glossing --------
LEIPZIG_GLOSSING = {
    "جب ہماری کلاس لگے کرے ای۔": {
        "urdu": "جب ہماری کلاس لگتی تھی۔",
        "english": "When our class used to take place.",
        "words": [
            ["جب", "SCONJ", "When"],
            ["ہماری", "1SG.POSS", "Our"],
            ["کلاس", "N", "Class"],
            ["لگے", "V-root+ASP", "Root verb + aspect suffix"],
            ["کرے", "V-root+HAB", "Habitual auxiliary"],
            ["ای", "COP.PST.FEM", "Copula (past feminine)"]
        ]
    },
    "کہ او کتنو پختو لکھار ی اے۔": {
        "urdu": "کہ وہ کتنا اچھا لکھاری ہے۔",
        "english": "That he is such a good writer.",
        "words": [
            ["کہ", "SCONJ", "That"],
            ["او", "PRON.3SG", "He/She"],
            ["کتنو پختو", "ADJ", "Good"],
            ["لکھاری", "N-AGENT-NOM", "Writer"],
            ["اے", "COP.PRES.3SG", "Is"]
        ]
    },
    "اگر وےیا لباس اے پہری راکھاں۔": {
        "urdu": "اگر وہ لباس کو پہنتے ہیں۔",
        "english": "If he wears those clothes.",
        "words": [
            ["اگر", "SCONJ", "If"],
            ["وے", "PRON.3SG", "He/She"],
            ["یا", "DEM", "That"],
            ["لباس اے", "N+DAT", "Clothes (dative)"],
            ["پہری راکھاں", "V-root+ASP+HAB", "Wear (progressive+habitual)"]
        ]
    },
    "گیانی اور تعلیم کا ماہر لوگن کو ای ماننواے اے۔": {
        "urdu": "گیانی اور تعلیم کے ماہر لوگوں کو یہ ماننا ہے۔",
        "english": "The people accept scholars and education experts.",
        "words": [
            ["گیانی", "N", "Scholar"],
            ["اور", "CONJ", "And"],
            ["تعلیم", "N", "Education"],
            ["کا", "GEN", "Of"],
            ["ماہر", "N", "Expert"],
            ["لوگن کو", "N-PL+DAT", "People (dative)"],
            ["ای", "DEM", "This"],
            ["ماننواے", "V-root+INF+AUX", "To accept"],
            ["اے", "COP.PRES.3SG", "Is"]
        ]
    },
    "میرے مارے بی اب تک ایک اچھنبو سوای اے۔": {
        "urdu": "میرے لیے بھی اب تک ایک حیرانگی سی ہے۔",
        "english": "Even for me until now, there is a strange feeling.",
        "words": [
            ["میرے مارے", "1SG.POSS+POSTP", "For me"],
            ["بی", "FOC-PARTICLE", "Also/even"],
            ["اب تک", "ADV", "Until now"],
            ["ایک", "NUM", "One"],
            ["اچھنبو سوای", "ADJ+POSTP", "Strange like"],
            ["اے", "COP.PRES.3SG", "Is"]
        ]
    },
    "دنیا آ جا ری ہی۔": {
        "urdu": "دنیا آ جا رہی ہے۔",
        "english": "The world is coming and going.",
        "words": [
            ["دنیا", "N", "World"],
            ["آ", "ASP-PREFIX", "Come"],
            ["جا", "V-ROOT", "Go"],
            ["ری", "PROG", "Progressive"],
            ["ہی", "COP.PRES.3SG", "Is"]
        ]
    },
    "کا ہم ماضی اے زندہ رکھ سکاں؟": {
        "urdu": "کیا ہم ماضی کو زندہ رکھ سکتے ہیں؟",
        "english": "Can we keep the past alive?",
        "words": [
            ["کا", "Q-PART", "Question"],
            ["ہم", "PRON.1PL", "We"],
            ["ماضی اے", "N+DAT", "Past (dative)"],
            ["زندہ", "ADJ", "Alive"],
            ["رکھ", "V-ROOT", "Keep"],
            ["سکاں", "AUX-MOD.PL", "Can"]
        ]
    },
    "کہا میو روس میں باولا ہو گا؟": {
        "urdu": "کیا میواتی روس میں پاگل ہوگئے؟",
        "english": "Have the Miwatis gone crazy in Russia?",
        "words": [
            ["کہا", "Q-PART", "Question"],
            ["میو", "N", "Mewati"],
            ["روس", "PROPN", "Russia"],
            ["میں", "LOC", "In"],
            ["باولا", "ADJ", "Crazy"],
            ["ہو گا", "AUX.FUT.PL", "Will be"]
        ]
    },
    "کہا پوچھو جائیگو قبر میں؟": {
        "urdu": "کیا پوچھا جائے گا قبر میں؟",
        "english": "Will it be asked in the grave?",
        "words": [
            ["کہا", "Q-PART", "What"],
            ["پوچھو", "V-IMP", "Ask"],
            ["جائیگو", "V-FUT-PASS", "Will be asked"],
            ["قبر", "N", "Grave"],
            ["میں", "LOC", "In"]
        ]
    },
    "او کہن جا رو اے؟": {
        "urdu": "وہ کہاں جا رہا ہے؟",
        "english": "Where is he going?",
        "words": [
            ["او", "PRON.3SG", "He"],
            ["کہن", "ADV-LOC", "Where"],
            ["جا رو", "V-ROOT+PROG", "Going"],
            ["اے", "COP.PRES.3SG", "Is"]
        ]
    },
    "تینے کہا کھایو؟": {
        "urdu": "تم نے کیا کھایا؟",
        "english": "What did you eat?",
        "words": [
            ["تینے", "PRON.2SG+ERG", "You (ergative)"],
            ["کہا", "Q-PART", "What"],
            ["کھایو", "V-PFV", "Ate"]
        ]
    },
    "ہم رات کب سویا ہا؟": {
        "urdu": "ہم رات کب سوئے تھے؟",
        "english": "When did we sleep at night?",
        "words": [
            ["ہم", "PRON.1PL", "We"],
            ["رات", "N", "Night"],
            ["کب", "ADV", "When"],
            ["سویا ہا", "V-PFV+AUX", "Slept (past)"]
        ]
    },
    "ای جاڑان کی بات ای۔": {
        "urdu": "یہ جاڑوں کی بات ہے۔",
        "english": "This is a matter of winters.",
        "words": [
            ["ای", "DEM", "This"],
            ["جاڑان کی", "N-GEN", "Of winters"],
            ["بات", "N", "Matter"],
            ["ای", "COP.PRES", "Is"]
        ]
    },
    "او اچھو آدمی ہو۔": {
        "urdu": "وہ اچھا آدمی تھا۔",
        "english": "He was a good man.",
        "words": [
            ["او", "PRON.3SG", "He"],
            ["اچھو", "ADJ", "Good"],
            ["آدمی", "N", "Man"],
            ["ہو", "COP.PST.MASC", "Was"]
        ]
    },
    "بیربانی بڑی ملوک ہی۔": {
        "urdu": "عورت بہت خوبصورت تھی۔",
        "english": "The woman was very beautiful.",
        "words": [
            ["بیربانی", "N", "Woman"],
            ["بڑی", "ADV", "Very"],
            ["ملوک", "ADJ", "Beautiful"],
            ["ہی", "COP.PST.FEM", "Was (fem.)"]
        ]
    },
    "بوڑھی اماں نے کدی کائی کی برائی نہ کری۔": {
        "urdu": "بوڑھی اماں نے کبھی کسی کی برائی نہیں کی۔",
        "english": "The old mother never did anyone any harm.",
        "words": [
            ["بوڑھی", "ADJ-FEM", "Old (fem.)"],
            ["اماں", "N", "Mother"],
            ["نے", "ERG", "Ergative"],
            ["کدی", "ADV", "Ever"],
            ["کائی کی", "PRON-POSS", "Someone’s"],
            ["برائی", "N", "Evil"],
            ["نہ", "NEG", "Not"],
            ["کری", "V-PST.FEM", "Did (fem.)"]
        ]
    },
    "میواتی زبان اپنی بقا کی جنگ لڑری اے۔": {
        "urdu": "میواتی زبان اپنی بقا کی جنگ لڑ رہی ہے۔",
        "english": "The Mewati language is fighting for its survival.",
        "words": [
            ["میواتی", "N-PROPN", "Mewati"],
            ["زبان", "N", "Language"],
            ["اپنی", "3SG.POSS", "Its"],
            ["بقا", "N", "Survival"],
            ["کی", "GEN", "Of"],
            ["جنگ", "N", "War"],
            ["لڑری", "V-root+PROG", "Fighting"],
            ["اے", "COP.PRES", "Is"]
        ]
    },
    "بزرگن کی بہت سی سنت ٹوٹتی دکھائی دے ری ہاں۔": {
        "urdu": "بزرگوں کی بہت سی سنت بکھرتی دکھائی دے رہی ہیں۔",
        "english": "Many traditions of the elders appear to be breaking.",
        "words": [
            ["بزرگن کی", "N-PL-GEN", "Of elders"],
            ["بہت سی", "ADV+CLF", "Many"],
            ["سنت", "N-PL", "Traditions"],
            ["ٹوٹتی", "V-PROG-FEM", "Breaking"],
            ["دکھائی دے", "V-light", "Appear"],
            ["ری", "AUX-PROG-FEM", "Prog. fem."],
            ["ہاں", "COP.PRES.PL", "Are"]
        ]
    },
    "گول مٹول سلونٹن سو بھر و چہرو۔": {
        "urdu": "گول مٹول جھریوں سے بھرا چہرہ۔",
        "english": "A round face full of wrinkles.",
        "words": [
            ["گول مٹول", "ADJ", "Round"],
            ["سلونٹن", "N-PL", "Wrinkles"],
            ["سو", "POSTP", "From"],
            ["بھر و", "V-PST", "Filled"],
            ["چہرو", "N", "Face"]
        ]
    },
    "کپڑا کی لوگڑی۔": {
        "urdu": "کپڑے کا دوپٹہ۔",
        "english": "Scarf made of cloth.",
        "words": [
            ["کپڑا", "N", "Cloth"],
            ["کی", "GEN", "Of"],
            ["لوگڑی", "N", "Scarf/Dupatta"]
        ]
    },
    "یا کا منہ سو۔": {
        "urdu": "اس کے منہ سے۔",
        "english": "From his/her mouth.",
        "words": [
            ["یا", "DEM", "This/That"],
            ["کا", "GEN", "Of"],
            ["منہ سو", "N+POSTP", "Mouth+from"]
        ]
    }
}


# -------- X-Bar Structures --------
XBAR_TREES = {
    "جب ہماری کلاس لگے کرے ای۔": "[CP [C جب]\n    [TP [DP [D ہماری] [NP [N کلاس]]]\n       [T' \n            [VP [V   لگے کرے ای]][T Past]]]]",

    "کہ او کتنو پختو لکھاری اے۔": "[CP [C کہ]\n    [TP [DP [D ∅] [NP او]]\n        [T'\n            [VP [DP [D ∅] [NP [AP کتنو پختو] [N' [N لکھاری]]]] [V اے]] [T ∅]]]]",

    "اگر وے یا لباس اے پہری راکھاں۔": "[CP [C اگر]\n    [TP [DP [D ∅] [NP وے]]\n        [T' \n            [VP [DP [D یا] [NP [N لباس]]]\n                [V پہری راکھاں ]][T Present]]]]]",

    "گیانی اور تعلیم کا ماہر لوگن کو ای ماننواے۔": "[TP\n   [DP \n      [DP \n         [NP [NP گیانی اور تعلیم] \n             [PP [P کا] [NP ماہر]]]]\n      [DP \n         [NP [NP لوگن] \n             [PP [P کو]]]]\n   ]\n\n   [T'\n      [VP \n         [V' [Dp ای] [V ماننواے]]]\n      [T Past]\n   ]\n]",

    "میرے مارے بی اب تک ایک اچھنبو سوای اے۔": "[TP [DP [D ∅] [N میرے مارے بی]] [T' [VP [V' [AdvP اب تک] [V' [DP [D ایک] [NP [AP اچھنبو] [N' [N سوای]]]] [V اے]]]] [T Present]]]",

    "دنیا آ جا ری ہی۔": "[TP [DP [D ∅] [NP دنیا]]\n    [T'  [VP  [V آ][V   جا  ری  ]][T Past]]]",

    "کا ہم ماضی زندہ رکھ سکاں؟": "[CP [C کا] [TP [DP [D ∅] [NP ہم]] [T' [VP [DP [D اے] [NP ماضی]][V' [V زندہ رکھ سکاں] ]] [T ∅]]]]",

    "کہا میو روس میں باولا ہو گا؟": "[CP [C کہا] [TP [DP [D ∅] [NP میو]] [T' [VP [V' [V باولا ہو گا]] [PP روس میں]] [T Past]]]]",

    "کہا پوچھو جائیگو قبر میں؟": "[CP [C کہا] [TP [DP ∅] [T' [VP [V' [V پوچھو جائیگو]] [PP قبر میں]] [T Future]]]]",

    "اوکہن جا رو اے؟": "[CP [DP [D ∅] [N او]] [C' [C کہن] [TP [DP ∅] [T' [AuxP  [VP [V جا]] [Aux رواے ]] [T Prog]]]]]\n\n[CP [Spec [DP [D ∅] [N او]]] [C' [C کہن] [TP [Spec [DP ∅]] [T' [T Prog] [AuxP [Aux' [Aux رواے] [VP [V' [V جا]]]]]]]]]",

    "تینے کہا کھایو؟": "[TP [DP [D ∅] [NP تینے]]\n    [T' [T ∅]\n        [VP [DP [D ∅] [NP کہا]] [V کھایو]]]]",

    "ہم رات کب سویا ہا؟": "[CP [C کب]\n    [TP [DP [D ∅] [NP ہم]]\n        [T' [T ہا]\n            [VP [AdvP رات] [V سویا]]]]]",

    "ای جاڑان کی بات ای۔": "[TP [Spec [DP [D ∅] [N ای]]] [T' [T ∅] [VP [V' [DP [D ∅] [NP [NP جاڑان] [PP [P کی] [NP بات]]]] [V ای]]]]]",

    "او اچھو آدمی ہو۔": "[TP [Spec [DP [D ∅] [N او]]] [T'  [VP [V'  [DP [D ∅] [NP [AP اچھو] [N آدمی]]][V ہو]]][T ∅]]]",

    "بیربانی بڑی ملوک ہی۔": "[TP [Spec [DP [D ∅] [NP بیربانی]]] [T'  [VP [V' [AP [A' [DegP بڑی] [A ملوک]]] [V ہی]]][T ∅]]]",

    "بوڑھی اماں نے کدی کائی کی برائی نہ کری۔": "[TP [Spec [DP [D ∅] [NP [AP بوڑھی] [N' [N اماں] [CaseP [Case نے]]]]]] [T'  [VP [AdvP کدی] [V' [DP [D ∅] [N کائی]] [V' [NP [N'  [PP [P کی] [NP ∅]]][N برائی]] [V' [AdvP نہ] [V کری]]]]][T Perf]]]",

    "میواتی زبان اپنی بقا کی جنگ لڑری اے۔": "[TP [DP [D ∅] [NP [AP میواتی] [N' [N زبان]]]]\n    [T' [T اے]\n        [VP [DP [D ∅] [NP [NP اپنی بقا] [PP [P کی] [NP جنگ]]]] [V لڑری]]]]",

    "بزرگن کی بہت سی سنت ٹوٹتی دکھائی دے ری ہاں۔": "[TP [DP [D ∅] [NP [NP بزرگن] [PP [P کی] [NP [AP بہت سی] [N' [N سنت]]]]]]\n    [T' [T ہاں]\n        [VP [V' [V ٹوٹتی]\n            [V' [V دکھائی]\n                [V' [V دے]\n                    [V' [V ری] [V ∅]]]]]]]]",

    "گول مٹول سلونٹن سو بھر و چہرو۔": "[TP [Spec [DP [D ∅] [NP [AP گول مٹول] [N' [AP سلونٹن سو بھر و] [N' [N چہرو]]]]]] [T' [T ∅] [VP ∅]]]",

    "کپڑا کی لوگڑی۔": "[TP [DP [D ∅] [NP [N' [N کپڑا] [PP [P کی] [NP [N لوگڑی]]]]]] [T' [T ∅] [VP ∅]]]",

    "یا کا منہ سو۔": "[TP [DP [D یا کا] [NP [N' [N منہ] [PP [P سو]]]]] [T' [T ∅] [VP ∅]]]"
}


def build_xbar_tree(tokens):
    if not tokens:
        tokens = ["—"]
    return Tree("TP", [
        Tree("DP", [tokens[0]]),
        Tree("T'", [
            Tree("T", ["…"]),
            Tree("VP", tokens[1:] if len(tokens) > 1 else ["…"])
        ])
    ])

# -------- GUI --------
class MewatiGUI:
    def __init__(self, master):
        self.root = master
        master.title("Mewati Language Model")

        # Title Label
        title_label = tk.Label(
            master,
            text="Mewati Language Model",
            font=("Times New Roman", 12, "bold"),
            fg="black",
            bg="#e8f0fe",
            pady=10
        )
        title_label.pack(fill="x")

        # Input Box
        tk.Label(master, text="Enter Mewati Sentence:").pack(anchor="w", padx=6, pady=(6, 2))
        self.text_entry = tk.Entry(master, width=80, font=("Times New Roman", 12))
        self.text_entry.pack(fill="x", padx=8)

        # Buttons
        self.btn_frame = tk.Frame(master, bg="#f9f9f9")
        self.btn_frame.pack(pady=8)

        self.buttons = {
            "Morphological Features": {"cmd": self.display_morpho, "color": "#ffefef"},
            "SpaCy Features": {"cmd": self.display_spacy_analysis, "color": "#e8ffe8"},
            "Leipzig Glossing": {"cmd": self.display_gloss, "color": "#e6f0ff"},
            "X-Bar Syntax Tree": {"cmd": self.display_tree, "color": "#fff5e6"},
            "Clear Input": {"cmd": self.clear_input, "color": "#f6eaff"}
        }

        for text, opts in self.buttons.items():
            b = tk.Button(
                self.btn_frame,
                text=text,
                command=lambda t=text, c=opts["cmd"]: self.run_with_status(t, c),
                bg=opts["color"],
                fg="black",
                font=("Times New Roman", 10, "bold"),
                relief="groove",
                padx=12, pady=6
            )
            b.pack(side=tk.LEFT, padx=6, pady=4)

    def run_with_status(self, button_text, func):
        self.root.config(cursor="watch")
        self.root.update()
        self.root.title(f"Searching: {button_text} ...")
        try:
            func()
        finally:
            self.root.config(cursor="")
            self.root.title("Mewati Language Model")

    def _get_input_sentence(self):
        return normalize_sentence(self.text_entry.get())

    def display_morpho(self):
        sent = self._get_input_sentence()
        if sent not in MORPH_FEATURES:
            messagebox.showerror("Not Found", f"No morphological features for:\n{sent}")
            return
        rows = MORPH_FEATURES[sent]
        headers = ["Word", "Root", "Morph Structure", "Phonemic Change", "Explanation"]
        show_table_popup(self.root, "Morphological Features", headers, rows)

    def display_spacy_analysis(self):
        sent = self._get_input_sentence()
        if sent not in SPACY_FEATURES:
            messagebox.showerror("Not Found", f"No SpaCy features for:\n{sent}")
            return
        rows = SPACY_FEATURES[sent]
        headers = ["Word", "Lemma", "POS", "Dependency", "Explanation", "Head"]
        show_table_popup(self.root, "SpaCy Features", headers, rows)

    def display_gloss(self):
        sent = self._get_input_sentence()
        if sent not in LEIPZIG_ENTRIES:
            messagebox.showerror("Not Found", f"No Leipzig glossing for:\n{sent}")
            return
        entry = LEIPZIG_ENTRIES[sent]

        headers = ["Item", "Value", "Meaning"]
        rows = [
            ["Mewati Sentence", sent, ""],
            ["Urdu Translation", entry["urdu"], ""],
            ["English Translation", entry["english"], ""],
            ["---", "---", "---"],
            ["Word", "Gloss", "Meaning"]
        ] + entry["words"]

        # Mark the "Word | Gloss | Meaning" row as a special header
        show_table_popup(self.root, "Leipzig Glossing", headers, rows, special_header_index=4)

    def display_tree(self):
        sent = self._get_input_sentence()
        tree = XBAR_TREES.get(sent, build_xbar_tree(sent.split()))

        top = tk.Toplevel(self.root)
        top.title("X-Bar Syntax Tree")

        # Add shaded title
        lbl = tk.Label(
            top,
            text="X-Bar Syntax Tree",
            font=("Times New Roman", 12, "bold"),
            bg="#cfe2ff",
            fg="black",
            pady=5
        )
        lbl.pack(fill="x")

        cf = CanvasFrame(top, width=300, height=250, closeenough=2)
        t = TreeWidget(cf.canvas(), tree)
        cf.add_widget(t, 30, 30)
        cf.pack(expand=True, fill="both")
        top.protocol("WM_DELETE_WINDOW", cf.destroy)

    def clear_input(self):
        self.text_entry.delete(0, tk.END)

# -------- Main --------
if __name__ == "__main__":
    root = tk.Tk()
    gui = MewatiGUI(root)
    root.mainloop()
