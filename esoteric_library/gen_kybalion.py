#!/usr/bin/env python3
"""Generate kybalion.json — imscribed catalog for The Kybalion (1912)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PHI = '⊙'
D, T, R, P, F, K, G, Gm, C, H, S, Om = (
    '𐑦','𐑸','𐑾','𐑹','ƒ^ż','Ç^@','𐑲','ɢ^ˌ','⊙','𐑫','𐑳','𐑭')
TIER, CSCORE = 'O_∞', 0.95

def entry(num, title, desc, text, notes=""):
    return {
        "name": f"kybalion_{num:02d}", "number": num, "title": title,
        "description": desc, "text": text,
        "⊢": D, "⊣": T, ">": R, "<": P, "⋈": F, "⊤": K, "∈": G,
        "∋": Gm, PHI: C, "⊥": H, "⊞": S, "◻": Om,
        "tier": TIER, "C_score": CSCORE, "notes": notes,
    }

chapters = []

chapters.append(entry(0,
    "Title Page",
    "The title page of The Kybalion — 'A Study of The Hermetic Philosophy of Ancient Egypt and Greece' by Three Initiates, dedicated to Hermes Trismegistus.",
    'THE KYBALION: A Study of The Hermetic Philosophy of Ancient Egypt and Greece. BY THREE INITIATES. "The lips of wisdom are closed, except to the ears of Understanding." THE YOGI PUBLICATION SOCIETY, MASONIC TEMPLE, CHICAGO, ILLINOIS [1912]. TO HERMES TRISMEGISTUS, KNOWN BY THE ANCIENT EGYPTIANS AS "THE GREAT GREAT" AND "MASTER OF MASTERS", THIS LITTLE VOLUME IS REVERENTLY DEDICATED.'))

chapters.append(entry(1,
    "Table of Contents",
    "The table of contents listing all 15 chapters of The Kybalion.",
    'Table of Contents: I. The Hermetic Philosophy; II. The Seven Hermetic Principles (1. Mentalism, 2. Correspondence, 3. Vibration, 4. Polarity, 5. Rhythm, 6. Cause and Effect, 7. Gender); III. Mental Transmutation; IV. The All; V. The Mental Universe; VI. The Divine Paradox; VII. "The All" in All; VIII. Planes of Correspondence; IX. Vibration; X. Polarity; XI. Rhythm; XII. Causation; XIII. Gender; XIV. Mental Gender; XV. Hermetic Axioms.'))

chapters.append(entry(2,
    "Introduction",
    "The Three Initiates introduce the Hermetic Teachings traced to Hermes Trismegistus, the Master of Masters.",
    'We take great pleasure in presenting to the attention of students and investigators of the Secret Doctrines this little work based upon the world-old Hermetic Teachings. The purpose of this work is not the enunciation of any special philosophy or doctrine, but rather to give to the students a statement of the Truth that will serve to reconcile the many bits of occult knowledge that they may have acquired. There is no portion of the occult teachings possessed by the world which have been so closely guarded as the fragments of the Hermetic Teachings which have come down to us over the tens of centuries since the lifetime of its great founder, Hermes Trismegistus, the "scribe of the gods." From lip to ear the truth has been handed down among the few.'))

chapters.append(entry(3,
    "Chapter I: The Hermetic Philosophy",
    "Hermes Trismegistus as the founder of occult wisdom; the Kybalion as a compilation of veiled Hermetic axioms passed from Master to student.",
    'From old Egypt have come the fundamental esoteric teachings. In ancient Egypt dwelt Hermes Trismegistus, the Master of Masters, the father of Occult Wisdom, founder of Astrology, discoverer of Alchemy. The Hermetic Teachings are found in all lands, among all religions, but never identified with any particular country or sect. In the early days there was a compilation of certain Basic Hermetic Doctrines known as "THE KYBALION." The legends of the "Philosopher\'s Stone" were allegories relating to the Transmutation of Mental Forces. "Where fall the footsteps of the Master, the ears of those ready for his Teaching open wide."'))

chapters.append(entry(4,
    "Chapter II: The Seven Hermetic Principles",
    "The central chapter enumerating all seven Hermetic Principles: Mentalism, Correspondence, Vibration, Polarity, Rhythm, Cause and Effect, and Gender.",
    '"The Principles of Truth are Seven; he who knows these, understandingly, possesses the Magic Key." 1. THE PRINCIPLE OF MENTALISM: "THE ALL IS MIND; The Universe is Mental." 2. THE PRINCIPLE OF CORRESPONDENCE: "As above, so below; as below, so above." 3. THE PRINCIPLE OF VIBRATION: "Nothing rests; everything moves; everything vibrates." 4. THE PRINCIPLE OF POLARITY: "Everything is dual; everything has poles; opposites are identical in nature but different in degree." 5. THE PRINCIPLE OF RHYTHM: "Everything flows out and in; all things rise and fall; rhythm compensates." 6. THE PRINCIPLE OF CAUSE AND EFFECT: "Every Cause has its Effect; nothing escapes the Law." 7. THE PRINCIPLE OF GENDER: "Gender is in everything; everything has its Masculine and Feminine Principles."'))

chapters.append(entry(5,
    "Chapter III: Mental Transmutation",
    "True alchemy is Mental Transmutation — the art of changing mental states through Will, Attention, and Vibration.",
    '"Mind (as well as metals and elements) may be transmuted, from state to state; degree to degree; condition to condition; pole to pole; vibration to vibration. True Hermetic Transmutation is a Mental Art." The ancients possessed knowledge of transcendental chemistry (alchemy) and transcendental psychology (mystic psychology). Mental Transmutation is the "Art of Mental Chemistry" — changing and transforming mental states. The Great Work is the transmutation of base mental states into gold.'))

chapters.append(entry(6,
    "Chapter IV: The All",
    "Examines THE ALL, the Substantial Reality underlying all manifestation — Infinite Living Mind, UNKNOWABLE in its inner nature.",
    '"Under, and back of, the Universe of Time, Space and Change, is ever to be found The Substantial Reality — the Fundamental Truth." All thinkers in all lands have assumed the necessity for postulating a Substantial Reality. The Hermetic Masters call it "THE ALL." The inner nature of THE ALL is UNKNOWABLE. The universe is a Mental Creation of THE ALL, subject to the Laws of Created Things. THE ALL is Infinite, Immutable, and its nature transcends human comprehension.'))

chapters.append(entry(7,
    "Chapter V: The Mental Universe",
    "The Universe is Mental — held in the Mind of THE ALL. It is not THE ALL itself but a mental creation within it.",
    '"The Universe is Mental — held in the Mind of THE ALL." THE ALL is SPIRIT — Infinite Living Mind. The universe must be a mental creation of THE ALL, a "Mental Image" in the Mind of THE ALL, just as characters exist in the mind of an author. The Principle of Correspondence: as above so below. Our own mental images are real to us yet exist only in our minds. So the universe is real to us yet is but a mental image in the Infinite Mind.'))

chapters.append(entry(8,
    "Chapter VI: The Divine Paradox",
    "The paradoxical nature of the universe: while unreal relative to THE ALL, it must be treated as real on its own plane.",
    '"The half-wise, recognizing the comparative unreality of the Universe, imagine that they may defy its Laws — such are vain and presumptuous fools. The truly wise, knowing the nature of the Universe, use Law against laws; the higher against the lower; and by the Art of Alchemy transmute that which is undesirable into that which is worthy." This is the Paradox: while to THE ALL the Universe is as a dream, yet to all that is Finite the Universe must be treated as Real. Beware of Half-Truths.'))

chapters.append(entry(9,
    "Chapter VII: ''The All'' in All",
    "THE ALL is in all, and all is in THE ALL — the immanence of the Infinite in every part of creation.",
    '"While All is in THE ALL, it is equally true that THE ALL is in ALL. To him who truly understands this truth hath come great knowledge." THE ALL is Imminent in its Universe, in every part, particle, unit or combination. As the author exists within each character of his creation — Othello, Hamlet, Lear — giving them their vitality, so does THE ALL exist within every part of the universe. Each particle contains the essence of THE ALL within it.'))

chapters.append(entry(10,
    "Chapter VIII: Planes of Correspondence",
    "The universe divided into Three Great Planes: Physical, Mental, and Spiritual, with correspondence between them.",
    '"As above, so below; as below, so above." This Principle embodies the truth that there is harmony, agreement and correspondence between the several planes of Manifestation. The universe may be divided into: 1. The Great Physical Plane; 2. The Great Mental Plane; 3. The Great Spiritual Plane. These are but ascending degrees of the great scale of Life. The student who understands this Principle can reason from the known to the unknown.'))

chapters.append(entry(11,
    "Chapter IX: Vibration",
    "The Principle of Vibration: nothing rests; everything moves; everything vibrates. All is modes of vibratory motion.",
    '"Nothing rests; everything moves; everything vibrates." Motion is manifest in everything in the Universe. The differences between manifestations of universal power are due entirely to the varying rate and mode of vibrations. Spirit is at one end of the Pole of Vibration; gross Matter at the other. The Principle also applies to Mental Phenomena — mental states correspond to degrees of vibration. Knowledge of this Principle enables the Hermetist to change his own mental vibrations by an effort of Will.'))

chapters.append(entry(12,
    "Chapter X: Polarity",
    "The Principle of Polarity: everything has poles; opposites are identical in nature but different in degree.",
    '"Everything is dual; everything has poles; everything has its pair of opposites; like and unlike are the same; opposites are identical in nature, but different in degree; extremes meet; all truths are but half-truths; all paradoxes may be reconciled." Heat and Cold are identical in nature — merely degrees. Light and Darkness, Spirit and Matter, Good and Evil — all are poles of the same thing. The mastery of Polarity enables the Hermetist to transmute one mental state into its opposite.'))

chapters.append(entry(13,
    "Chapter XI: Rhythm",
    "The Principle of Rhythm: everything flows out and in; all things rise and fall; the pendulum-swing manifests in everything.",
    '"Everything flows out and in; everything has its tides; all things rise and fall; the pendulum-swing manifests in everything; the measure of the swing to the right is the measure of the swing to the left; rhythm compensates." Universes are created, reach their extreme low point, and begin their upward swing. The Hermetist understands this law and by operating the Principle of Neutralization — rising mentally above the vibrations of the pendulum swing — he escapes the effects of Rhythm to a certain degree.'))

chapters.append(entry(14,
    "Chapter XII: Causation",
    "The Principle of Cause and Effect: everything happens according to Law; Chance is but a name for Law not recognized.",
    '"Every Cause has its Effect; every Effect has its Cause; everything happens according to Law; Chance is but a name for Law not recognized; there are many planes of causation, but nothing escapes the Law." Nothing happens by Chance. There are many planes of causation — the higher plane laws are not understood by those on lower planes. The Hermetist rises to higher planes and by understanding the laws of the higher plane becomes a Master on the lower planes.'))

chapters.append(entry(15,
    "Chapter XIII: Gender",
    "The Principle of Gender: Gender is in everything; everything has its Masculine and Feminine Principles on all planes.",
    '"Gender is in everything; everything has its Masculine and Feminine Principles; Gender manifests on all planes." Gender (from Latin: "to beget, to generate") is broader than Sex. The office of Gender is solely that of creating, producing, generating. Even in the constitution of the atom, negative corpuscles cluster around a positive one. The Masculine Principle is Positive, Creative, Directive; the Feminine Principle is Receptive, Generative.'))

chapters.append(entry(16,
    "Chapter XIV: Mental Gender",
    "The Gender Principle applied to Mind — the duality of objective/conscious mind (Masculine) and subjective/subconscious mind (Feminine).",
    'The Hermetic Philosophy teaches that the Principle of Gender manifests on the Mental Plane. The Masculine Principle corresponds to the Objective Mind, Conscious Mind, Voluntary Mind. The Feminine Principle corresponds to the Subjective Mind, Sub-conscious Mind, Passive Mind. The Masculine Mind has the power of Will, Initiation, Directive Energy. The Feminine Mind has the power of Receptivity, Intuition, Imagination. True Mental Creation requires the cooperation of both.'))

chapters.append(entry(17,
    "Chapter XV: Hermetic Axioms",
    "Final chapter collecting practical Hermetic Axioms for mental transmutation — changing mental states through vibration, polarity, and the Law of Use.",
    '"The possession of Knowledge, unless accompanied by a manifestation and expression in Action, is like the hoarding of precious metals — a vain and foolish thing." Key Axioms: "To change your mood or mental state — change your vibration." "To destroy an undesirable rate of mental vibration, concentrate upon the opposite pole." "To Transmute Mental Energy, first neutralize the Rhythm and then apply the Principle of Polarity — this is the Master Formula." "The wise man, knowing the nature of the Universe, uses Law against laws; the higher against the lower."'))

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kybalion.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(chapters, f, ensure_ascii=False, indent=2)
print(f"Wrote {len(chapters)} entries -> {out}")
for ch in chapters:
    print(f"  {ch['number']:2d}: {ch['title']}")
