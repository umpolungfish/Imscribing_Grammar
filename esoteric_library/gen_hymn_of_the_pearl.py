#!/usr/bin/env python3
"""Generate hymn_of_the_pearl.json — imscribed catalog entry for
The Hymn of the Pearl (Hymn of the Robe of Glory) from the Acts of Thomas,
translated by G.R.S. Mead, Fragments of a Faith Forgotten [1900].

One complete entry: the full Gnostic poem of the soul's descent and return.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PHI = '⊙'  # criticality key (compatible with all tools)

def entry(num, title, desc, text,
          D, T, R, P, F, K, G, Gm, C, H, S, Om,
          tier, cscore, notes=""):
    return {
        "name": f"hymn_of_the_pearl_{num:02d}",
        "number": num,
        "title": title,
        "description": desc,
        "text": text,
        "⊢": D, "⊣": T, "≻": R, "≺": P, "⋈": F,
        "⊤": K, "∈": G, "∋": Gm, PHI: C,
        "⊥": H, "⊞": S, "◻": Om,
        "tier": tier, "C_score": cscore, "notes": notes,
    }

HYMN_TEXT = """When I was a little child,
And dwelling in my kingdom, in my Father's house,
And in the wealth and the glories
Of my nurturers had my pleasure,
From the East, our home,
My parents, having equipped me, sent me forth.
And of the wealth of our treasury
They had tied up for me a load.
Large it was, yet light,
So that I might bear it unaided --
Gold of Beth-'Ellaye
And silver of Gazzak the great,
And rubies of India,
And agate from the land of Kushan,
And they girded me with adamant
Which can crush iron.
And they took off from me the bright robe,
Which in their love they had wrought for me,
And my purple toga,
Which was measured (and) woven to my stature.
And they made compact with me,
And wrote it in my heart that it should not be forgotten:
"If thou goest down into Egypt,
And bringest the one pearl,
Which is in the midst of the sea
Hard by the loud-breathing serpent,
(Then) shalt thou put on thy bright robe
And thy toga, which is laid over it,
And with thy Brother, our next in rank,
Thou shalt be heir in our kingdom."

I quitted the East (and) went down,
There being with me two messengers,
For the way was dangerous and difficult,
And I was young to tread it.
I passed the borders of Maishan,
The meeting place of the merchants of the East,
And I reached the land of Babel,
And I entered the walls of Sarbug.
I went down into Egypt,
And my companions parted from me.
I betook me straight to the serpent,
Hard by his dwelling I abode,
(Waiting) till he could slumber and sleep,
And I could take my pearl from him.

And when I was single and alone,
A stranger to those with whom I dwelt,
One of my race, a free-born man,
From among the Easterns, I beheld there --
A youth fair and well-favoured.
And he came and attached himself to me.
And I made him my intimate,
A comrade with whom I shared my merchandise.
I warned him against the Egyptians
And against consorting with the unclean;
And I put on a garb like theirs,
Lest they should insult me because I had come from afar,
To take away the pearl,
And (lest) they should arouse the serpent against me.

But in some way or other
They perceived that I was not their countryman;
So they dealt with me treacherously.
Moreover they gave me their food to eat.
I forgot that I was a son of kings,
And I served their king;
And I forgot the pearl,
For which my parents had sent me,
And by reason of the burden of their ways
I lay in a deep sleep.

But all those things that befell me,
My parents perceived and were grieved for me;
And a proclamation was made in our kingdom,
That all should speed to our gate,
King and princes of Parthia
And all the nobles of the East.
So they wove a plan on my behalf,
That I might not be left in Egypt,
And they wrote to me a letter,
And every noble signed his name thereto:
"From thy Father, the King of kings,
And thy Mother, the Mistress of the East,
And from thy Brother, our next in rank,
To thee our son, who art in Egypt, greeting!
Up and arise from thy sleep,
And listen to the words of our letter!
Call to mind that thou art a son of kings!
See the slavery -- whom thou servest!
Remember the pearl
For which thou didst speed to Egypt!
Think of thy bright robe,
And remember thy glorious toga,
Which thou shalt put on as thine adornment,
When thy name hath been read out in the list of the valiant,
And with thy Brother, our next in rank,
Thou shalt be king in our kingdom."

And my letter (was) a letter
Which the King sealed with his right hand,
(To keep it) from the wicked ones, the children of Babel,
And from the savage demons of Sarbug.
It flew in the likeness of an eagle,
The king of all birds;
It flew and alighted beside me,
And became all speech.
At its voice and the sound of its rustling,
I started and arose from my sleep.
I took it up and kissed it,
And loosed its seal, (and) read;
And according to what was traced on my heart
Were the words of my letter written.
I remembered that I was a son of kings,
And my free soul longed for its natural state.
I remembered the pearl,
For which I had been sent to Egypt,
And I began to charm him,
The terrible loud-breathing serpent.
I hushed him to sleep and lulled him to slumber;
For my Father's name I named over him,
And the name of our next in rank,
And of my Mother, the Queen of the East;
And I snatched away the pearl,
And turned to go back to my Father's house.
And their filthy and unclean garb
I stripped off, and left it in their country,
And I took my way straight to come
To the light of our home, the East.

And my letter, my awakener,
I found before me on the road,
And as with its voice it had awakened me,
(So) too with its light it was leading me.
Shone before me with its form,
And with its voice and its guidance,
It also encouraged me to speed,
And with its love was drawing me on.
I went forth, passed by Sarbug,
I left Babel on my left hand,
And reached Maishan the great,
The haven of the merchants,
That sitteth on the shore of the sea.

And my bright robe, which I had stripped off,
And the toga wherein it was wrapped,
From the heights of Hyrcania
My parents sent thither,
By the hand of their treasurers,
Who in their faithfulness could be trusted therewith.
And because I remembered not its fashion --
For in my childhood I had left it in my Father's house --
On a sudden as I faced it,
The garment seemed to me like a mirror of myself.
I saw it all in my whole self,
Moreover I faced my whole self in (facing) it.
For we were two in distinction,
And yet again one in one likeness.
And the treasurers also,
Who brought it to me, I saw in like manner,
That they were twain (yet) one likeness.
For one kingly sign was graven on them,
Of his hands that restored to me
My treasure and my wealth by means of them.

My bright embroidered robe,
Embroidered with glorious colours;
With gold and with beryls,
And rubies and agates
And sardonyxes varied in colour,
It also was made ready in its home on high.
And with stones of adamant
All its seams were fastened;
And the image of the King of kings was depicted in full all over it,
And like the sapphire stone also were its manifold hues.
Again I saw that all over it
The motions of knowledge were stirring,
And as if to speak
I saw it also making itself ready.
I heard the sound of its tones,
Which it uttered to those who brought it down.
And I also perceived in myself
That my stature was growing according to his labours.
And in its kingly motions
It was spreading itself out towards me,
And in the hands of its givers
It hastened that I might take it.
And me too my love urged on
That I should run to meet it and receive it;
And I stretched forth and received it,
With the beauty of its colours I adorned myself,
And my toga of brilliant colours
I cast around me, in its whole breadth.
I clothed myself therewith, and ascended
To the gate of salutation and homage;
I bowed my head, and did homage
To the Majesty of my Father who had sent it to me,
For I had done his commandments,
And he too had done what he promised,
And at the gate of his princes
I mingled with his nobles;
For he rejoiced in me and received me,
And I was with him in his kingdom.
And with the voice of praise
All his servants glorify him.
And he promised that also to the gate
Of the King of kings I should speed with him,
And bringing my gift and my pearl
I should appear with him before our King."""

chapters = [
    entry(1,
        "The Hymn of the Pearl (Hymn of the Robe of Glory)",
        "The complete Gnostic poem from the Acts of Thomas: the soul's descent from the Light into the body (Egypt), forgetfulness, awakening by the letter from the Father, the recovery of the pearl (Gnosis), and the glorious return to the Kingdom. Translated by G.R.S. Mead.",
        HYMN_TEXT,
        "𐑦", "𐑸", "𐑾", "𐑹", "⋈^ż", "⊤^@", "𐑲", "∋^ˌ",
        "⊙", "𐑫", "𐑳", "𐑭",
        "O_∞", 0.93,
        "Complete cycle: descent (incarnation), slumber (forgetfulness), awakener (letter/the call), recovery of pearl (gnosis), return and reunion with the heavenly robe (the true Self). The robe as mirror-of-self establishes ⊙ self-modeling criticality. The integer winding 𐑭 tracks the full circuit. The many heterogeneous elements (prince, serpent, pearls, Egypt, robe, twin, treasurers, letter, eagle) demand 𐑳. Bidirectional call-and-response 𐑾 for the Father's letter calling and the soul answering. Sequential poetic narrative ∋^ˌ."),
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hymn_of_the_pearl.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(chapters, f, ensure_ascii=False, indent=2)
print(f"Wrote {len(chapters)} entries -> {out}")