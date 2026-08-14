#!/usr/bin/env python3
"""Generate grimoires.json — imscribed catalog for grimoires.
Fill in the entries below, then run:
    python3 esoteric_library/gen_grimoires.py
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PHI = '⊙'  # criticality key (pre-migration, compatible with all tools)

def entry(num, title, desc, text,
          D, T, R, P, F, K, G, Gm, C, H, S, Om,
          tier, cscore, notes=""):
    return {
        "name": f"grimoires_{num:02d}",
        "number": num,
        "title": title,
        "description": desc,
        "text": text,
        "⊢": D, "⊣": T, "≻": R, "≺": P, "⋈": F,
        "⊤": K, "∈": G, "∋": Gm, PHI: C,
        "⊥": H, "⊞": S, "◻": Om,
        "tier": tier, "C_score": cscore, "notes": notes,
    }

chapters = [
    entry(1, "The Emerald Tablet (Tabula Smaragdina)",
        "The most famous alchemical text, attributed to Hermes Trismegistus. Core doctrine of the Hermetic tradition: 'As above, so below.'",
        """The Emerald Tablet of Hermes Trismegistus — the foundational text of Western alchemy and Hermetic philosophy. The Tablet probably first appeared in the West in editions of the pseudo-Aristotelian Secretum Secretorum (translated c. 1140). Its earliest Arabic recension appears in the Kitab Sirr al-Asar (c. 800 CE) and the Jabirian corpus.

Key text from the Jabir ibn Hayyan version:

Truth! Certainty! That in which there is no doubt! That which is above is from that which is below, and that which is below is from that which is above, working the miracles of the One. As all things were from One. Its father is the Sun and its mother the Moon. The Earth carried it in her belly, and the Wind nourished it in her belly, as Earth which shall become Fire. Feed the Earth from that which is subtle, with the greatest power. It ascends from the earth to the heaven and becomes ruler over that which is above and that which is below.

Another Arabic version adds: The structure of the microcosm is in accordance with the structure of the macrocosm. The force of forces overcomes every subtle thing and penetrates into everything gross. The light of lights within it makes the darkness flee before it.

This text encodes the entire alchemical Great Work in twelve cryptic axioms — the birth of the Philosopher's Stone from the union of Sun and Moon, the circulation of the elements, and the correspondence between celestial and terrestrial planes. Its rediscovery by Balinas (Apollonius of Tyana) in a hidden chamber beneath a statue of Hermes established the paradigm of the concealed wisdom tradition.""",
        "𐑼","𐑥","𐑽","𐑿","⋈^ì","⊤^@","𐑚","∋^Ş","𐑮","𐑖","𐑳","𐑴",
        "O₂", 0.65,
        "Classic ritual magic text. 𐑼 bounded ritual/spiritual space; 𐑥 crossing point between mundane and divine; 𐑽 adjoint invocation-response; 𐑿 quantum superposition of summoned/dismissed spirits; ⋈^ì classical fidelity through physical ritual; ⊤^@ slow kinetics requiring precise timing; 𐑚 localized to magician's circle; ∋^Ş broadcast addressing spiritual hierarchies; 𐑮 complex-plane critical at boundary of seen/unseen; 𐑖 two-step Markov (preparation then execution); 𐑳 many heterogeneous participants; 𐑴 Z2 parity (circle consecrated or not)."),

    entry(2, "The Book of the Sacred Magic of Abramelin the Mage",
        "A 15th-century grimoire translated by S.L. MacGregor Mathers. Massive influence on Aleister Crowley and the Hermetic Order of the Golden Dawn.",
        """The Book of the Sacred Magic of Abramelin the Mage, translated by S.L. MacGregor Mathers from a 15th-century French manuscript [1900]. This remarkable grimoire describes the quest of Abraham of Würzburg, a cabalist and scholar of magic, who sought the secret teachings across Europe before finding the magician Abramelin in Egypt.

The system involves many months of purification — a six-moon regimen of prayer, abstinence, and spiritual preparation — followed by the invocation of good and evil spirits to accomplish worldly goals including the acquisition of treasure, love, travel through the air and under water, and raising armies out of thin air. Also described are operations for raising the dead, transforming one's appearance, becoming invisible, and starting storms.

The key to the entire system is a set of remarkable magic squares — sigils consisting of mystical words readable in multiple directions. These word-squares encode the names of spirits and angels, and are said to have no potency unless used in the appropriate ritual context by an initiate who has completed the preparatory regimen. Mathers analyzed these squares extensively, giving possible derivations from Hebrew, Greek, and other languages.

The text is divided into three books: Book One describes Abraham's journey and his meeting with Abramelin; Book Two details the six-month operation and the preparation of the ritual space, including the selection of the place, the convocation of spirits, and how to resist their demands; Book Three contains the magical squares themselves. This work became a primary source for the ceremonial magic of the Golden Dawn and directly inspired Aleister Crowley's own magical system.""",
        "𐑼","𐑥","𐑽","𐑿","⋈^ì","⊤^@","𐑚","∋^Ş","𐑮","𐑖","𐑳","𐑴",
        "O₂", 0.65,
        "Tuple identical to all ritual grimoires: the adjoint invocation-response loop (𐑽) and Z2 circle-consecration symmetry (𐑴) are invariant across the genre."),

    entry(3, "The Key of Solomon the King (Clavicula Salomonis)",
        "The most famous grimoire of all. Translated by S. Liddell MacGregor Mathers [1888]. The foundational text of European ceremonial magic.",
        """The Key of Solomon the King (Clavicula Salomonis), translated and edited by S. Liddell MacGregor Mathers from ancient manuscripts in the British Museum [1888]. This is the most influential grimoire of the Western magical tradition — the foundational operational manual of ceremonial magic.

The work is divided into two books. Book I opens with the spiritual prerequisites: the Divine Love that must precede the Art. It details the days, hours, and planetary virtues; the confession to be made by the exorcist; the prayers and conjurations of increasing potency; and the construction of the holy Pentacles or Medals — the celestial seals by which spirits are bound. It includes experiments for recovering stolen goods, attaining invisibility, seeking favour and love, and mastering treasures guarded by spirits.

Book II is the technical manual of the Art: how the Master must govern himself; the fasting and observances; the baths and their arrangement; the garments, shoes, and vestments; the choice of place for operations; the instruments — knife, sword, sickle, poniard, lance, wand, staff; the formation of the Circle — the most crucial protective structure; the incenses, suffumigations, and perfumes; the water, hyssop, light, and fire; the pen, ink, and colours; virgin parchment; wax and virgin earth; the silken cloth; the consecration of the Magical Book; and the sacrifices to spirits.

The Key establishes the complete operative framework of Western magic: purification, consecration, invocation, and dismissal — all bounded by the Circle, armed with the Pentacles, and governed by the planetary hours. Its influence pervades every subsequent grimoire and magical order, from the Renaissance to the Golden Dawn and beyond.""",
        "𐑼","𐑥","𐑽","𐑿","⋈^ì","⊤^@","𐑚","∋^Ş","𐑮","𐑖","𐑳","𐑴",
        "O₂", 0.65,
        "The ur-text of ceremonial magic. Mathers' translation from multiple manuscript sources (Additional MSS 10862, Lansdowne MSS 1203) established the standard edition."),
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "grimoires.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(chapters, f, ensure_ascii=False, indent=2)
print(f"Wrote {len(chapters)} entries -> {out}")