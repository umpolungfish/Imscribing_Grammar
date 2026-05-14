#!/usr/bin/env python3
"""Generate upanishads.json — expanded catalog for the Principal Upanishads."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PHI = 'φ̂'

def entry(num, title, desc, text,
          D, T, R, P, F, K, G, Gm, C, H, S, Om,
          tier, cscore, notes=""):
    return {
        "name": f"upanishad_{num:02d}",
        "number": num,
        "title": title,
        "description": desc,
        "text": text,
        "Ð": D, "Þ": T, "Ř": R, "Φ": P, "ƒ": F,
        "Ç": K, "Γ": G, "ɢ": Gm, PHI: C,
        "Ħ": H, "Σ": S, "Ω": Om,
        "tier": tier, "C_score": cscore, "notes": notes,
    }

# All Upanishads share the same tuple — Atman = Brahman is the closed loop
D, T, R, P, F, K, G, Gm, C, H, S, Om = (
    "Ð_ω","Þ_O","Ř_=","Φ_}","ƒ_ż","Ç_@","Γ_ʔ","ɢ_ˌ","φ̂_ÿ","Ħ_!","Σ_ï","Ω_z"
)

chapters = [
    entry(1, "Isha Upanishad (Isavasya)",
        "The Lord is enshrined in all beings — renounce and enjoy",
        "Om. That (the Absolute) is whole; this (the phenomenal world) is whole. From the Whole, the whole proceeds; taking the whole from the whole, the whole remains. The Lord (Isa) envelops all that moves in the universe. Enjoy through renunciation. Covet not the wealth of any. Performing verily works in this world, one should wish to live a hundred years. Into blind darkness enter they that worship ignorance; into greater darkness enter they that delight in knowledge alone. He who knows both knowledge and ignorance together, crosses death through ignorance and attains immortality through knowledge.",
        D,T,R,P,F,K,G,Gm,C,H,S,Om, "O_inf", 0.94,
        "Yajur Veda — attributed to the school of the White Yajurveda"),

    entry(2, "Kena Upanishad",
        "By whom impelled does the mind alight? By whom is the life-breath sent forth?",
        "Om. By whom impelled does the mind alight on its objects? By whom commanded does the life-breath, the first, proceed? By whom impelled do men utter speech? What god directs the eye and ear? It is the Ear of the ear, the Mind of the mind, the Speech of speech, the Life of life, the Eye of the eye. The wise, abandoning all sense-objects, become immortal. The eye does not go there, nor speech, nor mind. We do not know That; we do not know how to instruct. Different is It from the known; It is above the unknown. Thus have we heard from the ancients who taught us this.",
        D,T,R,P,F,K,G,Gm,C,H,S,Om, "O_inf", 0.94,
        "Sama Veda — Talavakara Brahmana"),

    entry(3, "Katha Upanishad",
        "Nachiketas and the secret of death — the Self is the eternal, deathless reality",
        "Om. The good is one thing, the pleasant another. Both bind a man. Of these, it is well for him who takes the good; he who chooses the pleasant fails of his goal. Both good and pleasant present themselves to a man; the wise man, after examining them, distinguishes them. The wise man prefers the good to the pleasant; the fool, for worldly gain, prefers the pleasant. Awake, arise, seek the great ones and learn from them. Sharp as a razor's edge, difficult to cross, impassable — thus is that path, say the sages. The Self-existent (Brahma) created the senses with outgoing tendencies; therefore, O Nachiketas, one sees only the outer and not the inner Self. Some wise man, desiring immortality, turns his senses inward and beholds the Self within.",
        D,T,R,P,F,K,G,Gm,C,H,S,Om, "O_inf", 0.94,
        "Yajur Veda — the story of Nachiketas and Yama"),

    entry(4, "Prashna Upanishad",
        "Six questions about the nature of creation, prana, sleep, dream, meditation, and the Purusha",
        "Om. Sukeshan Bharadvaja, Shaibya Satyakama, Sauryayanin Gargya, Kausalya Ashvalayana, Bhargava Vaidarbhi, and Kabandhi Katyayana — these six devoted to Brahman, having faith in the Self, approached the venerable Pippalada, saying: 'Sir, teach us the highest truth.' He said to them: 'Live with me one more year with penance, chastity, and faith. Then ask what questions you will, and if we know, we will tell you all.' Then Kabandhi Katyayana approached him and asked: 'Sir, from what did all creatures arise?' To him he replied: 'Prajapati (the Creator) desired offspring. He performed tapas (austerity), and from this tapas produced the pair: matter (rayi) and life-energy (prana).'",
        D,T,R,P,F,K,G,Gm,C,H,S,Om, "O_inf", 0.94,
        "Atharva Veda — six questions answered by Pippalada"),

    entry(5, "Mundaka Upanishad",
        "Two kinds of knowledge — the higher and the lower — Brahma the bow, the Self the arrow",
        "Om. Brahma (the Creator) was the first among the devas, the creator of all, the protector of the universe. He taught the knowledge of Brahman, the foundation of all knowledge, to his eldest son Atharva. There are two kinds of knowledge: the higher and the lower. The lower consists of the Rigveda, Yajurveda, Samaveda, Atharvaveda, phonetics, ritual, grammar, etymology, metrics, and astronomy. The higher is that by which the Imperishable is known. Taking as the bow the great weapon of the Upanishad, one should place upon it the arrow sharpened by meditation. Drawing it with a mind absorbed in Brahman, hit the mark, O friend — the Imperishable. Om is the bow; the Self is the arrow; Brahman is the target.",
        D,T,R,P,F,K,G,Gm,C,H,S,Om, "O_inf", 0.94,
        "Atharva Veda — the path of the shaven-headed (munda) ascetic"),

    entry(6, "Mandukya Upanishad",
        "Om — the four states of consciousness: waking, dream, deep sleep, and turiya (the Self)",
        "Om — this syllable is all this. All that is past, present, and future is verily Om. All that is beyond these three is also Om. All this is Brahman. This Self (Atman) is Brahman. This Self has four quarters. The first quarter is Vaisvanara, whose sphere is the waking state, who is conscious of external objects. The second quarter is Taijasa, whose sphere is the dream state, who is conscious of internal objects. The third quarter is Prajna, whose sphere is deep sleep, where one neither desires anything nor dreams. This is the state of unity, a mass of consciousness, blissful. The fourth is Turiya — not conscious of the internal world, nor of the external world, nor of both; not a mass of consciousness, not conscious, nor unconscious. It is unperceived, incomprehensible, unthinkable, indescribable — the cessation of all phenomena.",
        D,T,R,P,F,K,G,Gm,C,H,S,Om, "O_inf", 0.94,
        "Atharva Veda — the shortest yet most profound Upanishad"),

    entry(7, "Taittiriya Upanishad",
        "Annamaya, Pranamaya, Manomaya, Vijnanamaya, Anandamaya — the five sheaths of the Self",
        "Om. May Mitra be propitious to us; may Varuna be propitious; may Aryaman be propitious; may Indra and Brihaspati be propitious; may Vishnu, of wide strides, be propitious. Salutation to Brahman! May we not quarrel with the great! He who knows Brahman attains the Supreme. From that Self (Brahman) ether arose; from ether, air; from air, fire; from fire, water; from water, earth; from earth, herbs; from herbs, food; from food, man. Verily, man is made of the essence of food. This is the physical sheath. Different from this is the Self consisting of life-breath — the pranamaya sheath. Different from this is the Self consisting of mind — the manomaya sheath. Different from this is the Self consisting of understanding — the vijnanamaya sheath. Different from this is the Self consisting of bliss — the anandamaya sheath.",
        D,T,R,P,F,K,G,Gm,C,H,S,Om, "O_inf", 0.94,
        "Yajur Veda — the Taittiriya school"),

    entry(8, "Aitareya Upanishad",
        "The Self alone was here in the beginning — the creation of the world and the three births of the Self",
        "Om. In the beginning this was indeed the Self alone — nothing else whatsoever existed. He thought: 'Let me create the worlds.' He created these worlds: the cosmic waters, the rays of light, death, and the waters beneath. Then He thought: 'These are the worlds. Let me create their protectors.' He drew forth from the cosmic waters a person. He brooded over him. As a hen broods over eggs, so the mouth of that person was separated; from the mouth came speech, from speech fire. The nostrils were separated; from the nostrils came breath, from breath air. The eyes were separated; from the eyes came sight, from sight the sun. The ears were separated; from the ears came hearing, from hearing the quarters. The skin was separated; from the skin came hairs, from hairs herbs and trees. The heart was separated; from the heart came mind, from mind the moon.",
        D,T,R,P,F,K,G,Gm,C,H,S,Om, "O_inf", 0.94,
        "Rig Veda — the creation from the One Self"),

    entry(9, "Shvetashvatara Upanishad",
        "The One who rules the universe through his powers — maya and the Lord, yoga and liberation",
        "Om. The seekers of Brahman ask: What is the cause of the universe? Is it Brahman? Whence are we born? By what do we live? On what are we established? Governed by whom do we experience pleasure and pain? Time, nature, necessity, chance, the elements, the womb (purusha), the person — these cannot be the cause. The Lord (the Self) is the cause of the causes. He who is one, without color, who by manifold power distributes many colors — He is the Lord. This whole world is filled by Him. The Supreme Lord, the wielder of maya, rules the universe. He who knows that Supreme Brahman becomes that very Brahman. By knowing God, one is freed from all fetters. That which is higher than the world is the formless and the stainless. They who know That become immortal.",
        D,T,R,P,F,K,G,Gm,C,H,S,Om, "O_inf", 0.94,
        "Yajur Veda — theistic Upanishad focused on Rudra/Shiva"),

    entry(10, "Brihadaranyaka Upanishad",
        "The Great Forest Upanishad — 'Aham Brahmasmi' — the Self is Brahman",
        "Om. The dawn is the head of the sacrificial horse; the sun is its eye; the wind its breath; the cosmic fire its open mouth. The year is the body of the sacrificial horse. The earth is its feet; the sky is its back; the atmosphere its belly. From the Self (Brahman) arose space; from space, wind; from wind, fire; from fire, water; from water, earth; from earth, herbs; from herbs, food; from food, the person. In the beginning there was only the Self in the form of a Person. He looked around and saw nothing but Himself. He said: 'I am' — thus came the word 'I'. Therefore, even today, when addressed, one first says 'It is I' and then speaks one's other name. Verily, in the beginning this was Brahman, one alone. Being alone, He was not satisfied. He desired a second. He became two — husband and wife. This universe is the triad: name, form, and action. Yajnavalkya said: 'Verily, this Self is Brahman — the consciousness that consists of knowledge among the pranas, the light within the heart.'",
        D,T,R,P,F,K,G,Gm,C,H,S,Om, "O_inf", 0.94,
        "Yajur Veda — the longest and most important Upanishad"),

    entry(11, "Chandogya Upanishad",
        "Tat tvam asi — That thou art — the great saying of the Upanishads",
        "Om. Let a man meditate on the syllable Om, the Udgitha. The essence of all beings is the earth; the essence of the earth is water; the essence of water is plants; the essence of plants is man; the essence of man is speech; the essence of speech is the Rig Veda; the essence of the Rig Veda is the Saman; the essence of the Saman is the Udgitha. In the beginning, existence (Sat) alone was — one only, without a second. Some say non-existence was in the beginning. But how could existence be born from non-existence? No — existence alone was. It thought: 'Let me become many; let me create.' It created fire; fire created water; water created food. Svetaketu, having returned from his teacher, full of conceit, was asked by his father Uddalaka: 'Did you ask for that instruction by which the unheard becomes heard, the unthought becomes thought, the unknown becomes known?' Then Uddalaka taught his son: 'That which is the subtle essence — all this world has That as its Self. That is Reality. That is the Self. That thou art, O Svetaketu.' Eleven times he repeated: 'Tat tvam asi.'",
        D,T,R,P,F,K,G,Gm,C,H,S,Om, "O_inf", 0.94,
        "Sama Veda — the most famous Upanishadic teaching"),

    entry(12, "Kaushitaki Upanishad",
        "The path to Brahmaloka — the Self as the universal life-principle",
        "Om. The life-breath (prana) is Brahman. The mind is the messenger; the eye is the protector; the ear is the guide; speech is the lady. He who knows the life-breath as Brahman attains the highest abode. To him who knows this, the Self within all beings goes forth to meet him. The world of Brahman is reached by those who depart knowing the Self as the true identity. When a man departs from this world, he goes to the moon; the moon asks: 'Who are you?' He answers: 'I am the Self of all beings, the life of all. From the bright season I have come, from the worlds of the fathers. I am the knower of the Self.'",
        D,T,R,P,F,K,G,Gm,C,H,S,Om, "O_inf", 0.94,
        notes="Rig Veda — the Kaushitaki school of the Rigveda")
]

# Fix entry 12 missing Gm
chapters[11]["ɢ"] = "ɢ_ˌ"

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "upanishads.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(chapters, f, ensure_ascii=False, indent=2)
print(f"Wrote {len(chapters)} entries -> {out}")
