#!/usr/bin/env python3
"""Generate hermetica.json — imscribed catalog for hermetica corpus.
Corpus Hermeticum entries from G.R.S. Mead's Thrice-Greatest Hermes, Vol. 2 [1906].
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PHI = '⊙'

def entry(num, title, desc, text,
          D, T, R, P, F, K, G, Gm, C, H, S, Om,
          tier, cscore, notes=""):
    return {
        "name": f"hermetica_{num:02d}",
        "number": num,
        "title": title,
        "description": desc,
        "text": text,
        "Ð": D, "Þ": T, "Ř": R, "Φ": P, "ƒ": F,
        "Ç": K, "Γ": G, "ɢ": Gm, PHI: C,
        "Ħ": H, "Σ": S, "Ω": Om,
        "tier": tier, "C_score": cscore, "notes": notes,
    }

HERM_TUPLE = {
    "D": "Ð_ω", "T": "Þ_O", "R": "Ř_=", "P": "Φ_}",
    "F": "ƒ^ż", "K": "Ç^@", "G": "Γ_ʔ", "Gm": "ɢ^ˌ",
    "C": "⊙_ÿ", "H": "Ħ_!", "S": "Σ_ï", "Om": "Ω_z",
    "tier": "O_inf", "cscore": 0.94
}

chapters = [
    entry(1,
        "Poimandres, the Shepherd of Men",
        "The visionary opening revelation: Hermes beholds the Mind of the Universe, who reveals the creation of the cosmos and God as Light and Life.",
        "1. It chanced once on a time my mind was meditating on the things that are, my thought was raised to a great height, the senses of my body being held back—just as men are who are weighed down with sleep after a fill of food. Methought a Being more than vast, in size beyond all bounds, called out my name and saith: What wouldst thou hear and see? I am Man-Shepherd, Mind of all-masterhood. I reply: I long to learn the things that are, and comprehend their nature, and know God. Then saith Man-Shepherd: That Light am I, thy God, Mind, prior to Moist Nature which appeared from Darkness; the Light-Word that appeared from Mind is Son of God. Not separate are they the one from other.",
        **HERM_TUPLE,
        notes="The foundational Hermetic revelation. Poimandres = the Mind of Sovereignty."),

    entry(2,
        "The General Sermon",
        "On God and creation. The text is lost from the Greek Corpus, preserved only by title through Psellus.",
        "NOTE: The title only is preserved in our Corpus, the text having disappeared with the loss of a quire before the parent copy came into the hands of Psellus. However, Hermes teaches throughout: The Glory of all things is God. Source of the things that are is God, who is both Mind and Nature—yea Matter, the Wisdom that reveals all things. For God is the All, and the All is God. What is above the heavens is God; what is below the heavens is the All. The Good is in God alone; the Cosmos is the Plenitude of God, while God is the Good of the Cosmos.",
        **HERM_TUPLE,
        notes="Text lost — only the title preserved by Psellus in the Greek Corpus."),

    entry(3,
        "The Sacred Sermon of Hermes to Asclepius",
        "On creation: the Glory of God as Source, the emergence of Light from the Abyss, and the ordering through seven circles of Heaven.",
        "The Glory of all things is God, Godhead and Godly Nature. Source of the things that are is God, who is both Mind and Nature—yea Matter, the Wisdom that reveals all things. Darkness that knew no bounds was in Abyss, and Water too and subtle Breath intelligent; these were by Power of God in Chaos. Then Holy Light arose; and there collected 'neath Dry Space from out Moist Essence Elements. And Heaven was seen in seven circles; its Gods were visible in forms of stars with all their signs. And every God by his own proper power brought forth what was appointed him.",
        **HERM_TUPLE,
        notes="Corpus Hermeticum III (IV.) — the Sacred Sermon."),

    entry(4,
        "The Cup or Monad",
        "Hermes to Tat: God's body is invisible and immeasurable, and He sent forth a Cup filled with Mind as a prize for souls.",
        "With Reason, not with hands, did the World-maker make the universal World; so that thou shouldst think of Him as everywhere and ever-being, the Author of all things, One and Only, who by His Will all beings hath created. This Body of Him is a thing no man can touch, or see, or measure, a Body inextensible, like to no other frame. 'Tis neither Fire nor Water, Air nor Breath; yet all of them come from it. He tilled a mighty Cup with Mind, and sent it down, joining a Herald to it, to proclaim: Baptize thyself with this Cup's draught, thou who hast faith to return to Him who sent the Cup.",
        **HERM_TUPLE,
        notes="Corpus Hermeticum IV (V.) — the baptism of Mind."),

    entry(5,
        "The Key",
        "Hermes to Tat on God as Father and the Good: God's energy is His Will, His essence is to will the being of all things.",
        "God, Father and the Good, hath the same nature, or more exactly, energy. God's energy is then His Will; further His essence is to will the being of all things. For what is God and Father and the Good but the to be of all that are not yet? Subsistence self of everything that is—this, then, is God, this Father, this the Good; to Him is added naught of all the rest. And though the Cosmos is also sire to them that share in him, yet he is not the cause of good unto the lives; he is sire only by the compulsion of the Good's Good-will, apart from which nor being nor becoming could ever be.",
        **HERM_TUPLE,
        notes="Corpus Hermeticum X (XI.) — the abridgment of the General Sermons."),

    entry(6,
        "In God Alone is Good",
        "A sermon to Asclepius: Good is in none else save God alone. The Good is essence free from motion; all subject to birth abounds in passions.",
        "Good, O Asclepius, is in none else save God alone; nay, rather, Good is God Himself eternally. If it be so, Good must be essence, from every kind of motion and becoming free, possessed of stable energy around Itself, never too little nor too much, an ever-full supply. Though one, yet is It source of all. For He stands not in need of any thing, so that desiring it He should be bad; nor can a single thing be lost to Him, on losing which He should be pained. For things subject to birth abound in passions. Where there's passion, nowhere is there Good.",
        **HERM_TUPLE,
        notes="Corpus Hermeticum VI (VII.) — the Good as sole attribute of God."),

    entry(7,
        "The Secret Sermon on the Mountain",
        "Tat beseeches Hermes for the teaching on Rebirth: the seed is the True Good, the womb is Wisdom-in-Silence, the sower is the Will of God.",
        "Tat saith: In the General Sermons, father, thou didst speak in riddles most unclear; when thou saidst no man could ever be saved before Rebirth, thy meaning thou didst hide. I know not from out what matter and what womb Man comes to birth. Hermes saith: Wisdom that understands in silence — such is the matter and the womb, and the True Good the seed. Tat saith: Who is the sower? Hermes saith: It is the Will of God, my son. The one begot will be another one from God, God's Son. All in all, out of all powers composed. Now, my son, keep silence and the birth divine shall be perfected in thee.",
        **HERM_TUPLE,
        notes="Corpus Hermeticum XIII (XIV.) — the mystery of palingenesis."),

    entry(8,
        "The Perfect Sermon (Asclepius I)",
        "The first part of the Asclepius: Hermes teaches Asclepius about God, the One and the All, and the eye of intellect.",
        "God, O Asclepius, hath brought thee unto us that thou mayest hear a Godly sermon, more Godly than the piety of ordinary faith. If thou with eye of intellect shalt see this Word thou shalt in thy whole mind be filled with all things good. If that, indeed, the many be the good, and not the one, in which are all. Indeed the difference between the two is found in their agreement — All is of One or One is All. So closely bound is each to other, that neither can be parted from its mate.",
        **HERM_TUPLE,
        notes="The Asclepius (Latin original lost; survives in Latin translation only). Part I."),

    entry(9,
        "The Perfect Sermon (Asclepius II)",
        "The conclusion of the Perfect Sermon: the Aeon as God's image, and the prophecy of restoration.",
        "O Asclepius, the Aeon is God's image, while Cosmos is the Aeon's image; the Sun is Cosmos' image, while Man is Sun's image. All things depend on the will of God. The Master of Eternity is God, who is one, and who is all. He has filled all things with His presence. He is the Father of all things, and the Good of all things, and the Life of all things. For this is the glory of all things — that God should be present in them. But the time draws near when men shall think that God is powerless; then shall the old order pass away, and God shall restore all things to their pristine beauty.",
        **HERM_TUPLE,
        notes="Asclepius conclusion — includes the prophecy of the fall of Egypt."),

    entry(10,
        "The Definitions of Asclepius",
        "Asclepius writes to King Ammon: a summing up of Hermetic teachings, with a warning against Greek translation.",
        "Great is the sermon which I send to thee, O King — the summing up and digest of all the rest. For it is not composed to suit the many's prejudice, since it contains much that refuteth them. Hermes, my master, hath said that unto those who come across my books, their composition will seem most simple and clear; but as 'tis unclear and has its inner meaning concealed, it will be still unclearer when the Greeks turn our tongue into their own. The Greeks have novel words, energic of argumentation only; but we do not use words, but use sounds full-filled with deeds. I begin by invocation to God, the universals' Lord and Maker, who though being All is One.",
        **HERM_TUPLE,
        notes="Corpus Hermeticum (XVI.) — Asclepius' letter to King Ammon."),
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hermetica.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(chapters, f, ensure_ascii=False, indent=2)
print(f"Wrote {len(chapters)} entries -> {out}")
