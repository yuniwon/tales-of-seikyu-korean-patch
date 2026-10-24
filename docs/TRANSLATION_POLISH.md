# Translation Polish Handoff

Updated: 2026-10-24. Editorial checkpoint and subsequent v0.1.18 release handoff.

Editorial review is complete through212:23,500 original occurrences, all1,381 AVG
groups and85 non-AVG tables, no unclassified rows, holds or open editorial callbacks.
See the game's quality_audit_20261023/FINAL_POLISH_AUDIT.md and completion_review.json.
Earlier checkpoint statements below are historical, not the current completion state.
Source/runtime issues remain in SOURCE_DATA_ISSUES.md; no gameplay completion claim.

Release v0.1.18 preserves this editorial checkpoint separately. The release payload
adds version metadata and retains the pre-existing English workaround on precisely
three inventory sort labels (Normal/Quest/Gold); their approved Korean remains in
the TSV. verify_polish_release.py normalizes only those three exact keys and then
requires the complete editorial row hash to match. All other source identities,
fingerprints and approved wording must remain byte-identical at the row-data level.
The frozen completion/history hashes describe the archived editorial payload,
not the release payload. See docs/release-v0.1.18.md for release/runtime evidence.
The release EXE was also installed in the local game:22,555 readbacks match,
font references pass and the game process survived a15-second startup smoke.
This does not supersede the recorded limits on actual visual gameplay testing.

## Forward Source Of Truth

`payload/reviewed_polish.tsv` is the cumulative approved text overlay. It is
consumed by `tools/generate_payload.py` after source-update overlays and source
fingerprinting. Do not manually edit `patch_payload.json` or rebuild approvals
by blindly replaying historical proposal directories.

Each row retains its source fingerprint, exact occurrence identity, original
Korean, approved Korean, review batch and rationale. Existing research and
completed translation worksets remain historical evidence, not competing
authoritative versions of these accepted rows.

To continue polishing, read a complete scene including choices and responses,
append approved changes to this file, preserve the original `old_target` when
refining an already accepted row, and regenerate:

```powershell
python -X utf8 tools/generate_payload.py
python -X utf8 tools/test_reviewed_polish.py
```

The generator rejects missing/ambiguous identities, duplicate approvals,
changed source fingerprints, concurrent Korean edits, and damaged tokens.
Already-applied rows are idempotent. A known patched installation is read from
a full-hash-verified clean backup; the installed game is not changed.

Missing payload rows require an exact original-row contract in
`payload/reviewed_additions.json`, plus an approved TSV translation whose
`old_target` is the verified original Japanese. No Korean is duplicated in the
registry. Additions cannot guess moved keys, reset concurrent Korean, or bypass
ordinary token/source checks. The frozen audit baseline remains unchanged.

## Current Accepted Batches

- 4,957 approved occurrences:4,955 net changes and two exact baseline restorations,
  including earlier audited fixes and twenty-four
  explicitly registered previously missing payload rows.
- 1,381 full scene groups / 18,250 AVG occurrences classified; all 1,381 groups are
  hold-free. AVG versus frozen pre-polish Korean: revised3,771,
  keep_verified14,479, hold0. Counts come from current verifier, not the sum of
  latest batch revisions: older representative approvals enter full-scene coverage.
- A final continuity reread does not reset an earlier correction to unchanged
  in cumulative counts. Latest-pass decisions are reported separately.
- Non-AVG:5,250/5,250 rows across85 complete tables including all1,105 custom UI rows,
  revised1,184/keep4,066/hold0. Seven structural interest_info references verified intact.
  Item names883/883 and descriptions875/875 fully classified.
  Description977 translation hold resolved with actual coffee consumer739 in185;
  contradictory coin251 source wiring remains documented, NOT fixed.
  Combined unique coverage23,500/23,500, net revised4,955/keep18,545/hold0.
  Approval history retains two exact returns to baseline, not net changed rows.
  Reviewed AVG flows and non-AVG tables are counted separately; a repeated
  scene reread adds no new source coverage.
- Initial Kincho hot-spring/tavern: 55 rows, revised 32 / keep 23.
- Batch003 Kincho hearts/wedding: 145 rows, revised 54 / keep 91.
- Batch004 Kincho farm/chickens/sleepover: 112 rows, revised 51 / keep 61.
  One already-approved row was refined; its original old_target is preserved.
- Batch005 Musashi hot-spring/tavern/sleepover: 89 rows, revised 28 / keep 61.
- Batch006 Musashi heart identity/family arc: all 267 mixed-cast rows,
  revised 41 / keep 226. Do not count only the 87 Musashi-spoken lines.
- Batch007 Sasaki craft/guardian/Seiryu origin heart: 272 rows,
  revised 72 / keep 200.
- Batch008 Sasaki proposal/dates/sleepover/wedding: 120 rows,
  revised 29 / keep 91.
- Batch009 Shuten family meals/proposal/dates/sleepover/wedding: 188 rows,
  revised 37 / keep 150 / hold 1.
- Batch010 continuity reread of these 580 rows: 9 additional refinements.
  Do not add those same occurrences to coverage a second time.
- Batch011 Shuten family/heist/origin heart: all 356 mixed-cast rows,
  revised 77 / keep 279. Restore the mother's invention, family grief and
  Red Oni relationship without erasing intentional unreliable narration.
- Batch012 Kincho/Shuten wedding reread: 125 already-classified rows,
  revised 2 / keep 123. One prior approval refined and one new approval;
  the Batch009 token hold is resolved. No new coverage counted.
- Batch013 CH2B_Q2.8/2.9/2.10 day off, duel and earthquake rescue:
  202 rows, revised 55 / keep 147. Restore duel motives, cancellation,
  leadership succession, rescue actions and speaker/addressee roles.
- Batch014 CH2B_Q2.13/2.14 lighthouse, Umibozu and Namazu:
  203 rows, revised 42 / keep 161. Restore location/name distinctions,
  conditional permission, hunger dialogue and fire-spreading objective.
- Batch015 CH3_Q3.1/3.2/3.2_Trials snow, dream and ancestor trial setup:
  192 rows, revised 35 / keep 157. Remove Japanese first-person residue,
  restore power/recruitment intent and distinguish all trials from Family Trial.
- Batch016 CH3_Q3.3/3.4/3.5 family, friendship and love trials:
  136 rows, revised 29 / keep 107. Repair dynamic-name particles,
  family/relationship nuance and the copied neighboring objective in row20158.
- Batch017 CH3_Q3.6/3.7/3.7_SeabertWorry/3.7_Workshop:
  212 rows, revised 42 / keep 170. Restore Kincho's excluded plans and
  injured Anji (not damaged hideout), correct adjacent copied dialogue,
  retain magic-circle coercion and present-tense parental love.
- Batch018 CH3_Q3.8/3.9/3.10 reunion, climax and cleansing setup:
  234 rows, revised 41 / keep 193, including appended31316-31320.
  Distinguish proxy speaker fields from displayed parent/Inari roles,
  ritual branches and causal uncertainty; retain separate climax variants.
- Source-only punctuation, numerals/countdowns and placeholders require no
  Korean payload entry but are classified and read in context.
- Batch019 CH3_YakanReturn / CH3_KonHero: 211 rows, revised 40 / keep 171.
  Repair copied hero introductions and source-token contamination; retain
  parental/Inari proxy roles, uncertain return timing and family affection.
- Batch020 CH3_TsukimiFestival: all 268 rows, revised 39 / keep 229.
  Preserve deliberate mask performances and flirtation; distinguish ema boards
  from the wish box, restore prank/spicy-wordplay callbacks and blessing duration.
- Batch021 18 lover endings plus closed ruins/dark-room fog: 161 rows,
  revised 38 / keep 123. Restore Kincho's truncated invitations and family/peace
  joke, Tor's baby-pirate joke, name particles and Yuki's first-person Korean.
  Keep distinct intimate voices and future-family possibilities, not present children.
- Batch022 seven opening/arrival/scroll groups: 197 rows, revised 38 / keep 159.
  Restore cake chronology, Seabert's self-reassurance and deliberate greeting mixup,
  farmhouse gift and selling cues. Includes late appended fishing-contest31354/31355.
- Batch023 CH2A Q1/Q2.2 tavern and illness investigation: 150 rows,
  revised 39 / keep 111. Restore truncated clan/contest/apology explanations,
  reversed accusation, own departure and Spanish-only player-token contamination.
- Batch024 CH2A Q2.3 secret base/full TRPG: 186 rows, revised 42 / keep 144.
  Forty new approvals and two refinements retaining original old_target. Restore
  poison denial, healer action, physical fence versus invented stolen-goods dealer,
  discount addressee and in-character voice; preserve every game branch.
- Batch025 CH2A Q2.4/2.5/2.6/2.6_1/2.7: 231 rows, revised 44 / keep 187.
  Restore ritual care roles, legends/secrecy limitations, other-form distinction,
  shared responsibility comparison, solve-riddle requirement and recovery banter.
  Keep own-victory and Nyotengu-cover escape alternatives separately keyed.
- Retained source conflicts: the localized hot-spring refusal follows aligned
  Japanese/English, not the older Chinese familiarity explanation.
- Historic held proposals25246/23040/23078 resolved through whole-scene review
  in Batches029/030, not blind acceptance of old proposals.
- 3,673 AVG rows remain unclassified, plus 5,250 non-AVG source rows in the
  full scope. Earlier exploratory audit reading is not full-polish completion.

Each packet has an immutable before payload/overlay, review configuration,
row-level decisions and merge receipt under the game audit's batchNNN folder.
Use `tools/merge_polish_scene_batch.py <batch.json> --apply` after reading the
entire packet. It checks the exact input payload hash, source fingerprints,
tokens, original approval history and exact post-generation row diff.

Resolved token issue: mixed-locale Korean wedding token unions were restored
to each row's exact Japanese-slot source contract. `Wedding_Shuten` row 26953
uses `{c.playername}` and `{npc.WeddingNPC}`; `Wedding_Kincho` row 26509 uses
only `{start_wedding_npc}`. The generator permits this source-backed repair
only for the two exact stable identities, pinned original source tokens and
known mixed-token input. All other token additions/loss/reordering and tag loss
remain rejected; source fingerprints remain mandatory. No runtime parser was
changed and no in-game wedding playback was performed. Cross-locale differences
elsewhere are not automatically defects.

Additional exact repair: CH3_Q3.5 row20158 / stable1809595912229486 is brief
agreement with no tokens in all six populated source languages. Its previous
Korean copied row20159's six-item objective and two BestLoverNpc tokens. The
repair removes that exact known contamination only; a different source token,
old-token pattern, new token or unreviewed identity is rejected. Source
fingerprints and prior-Korean concurrency checks still apply. Row20159 retains
three liked and three disliked items. The allowlist stores per-identity known
contaminated and canonical token tuples, including the two wedding repairs.

Batch017 exact adjacent-copy repairs: row20310/stable1814629625282673 restores
Seabert's invitation and removes shiver tags copied from Kon20311;
row20318/stable1814630351499405 restores a game-invitation choice and removes
the player placeholder copied from Kon20319; row20319/stable1814630351499407
restores Kon's complaint with its original missing player placeholder. All six
source locales corroborate these contracts. Same-token copied texts20321/20324
use ordinary corrections.

Batch019 exact adjacent-copy repairs: row19693/stable1814712403374107 restores
Yui's original shiver tag pair; row19695/stable1814712404686878 removes the player
placeholder copied into silence; row19700/stable1814712406960167 removes italic
tags copied from the next line into hesitation. All six source locales support
these contracts. All nine exact allowlisted repairs are tested for idempotence,
changed source/target rejection and non-transfer to other identities.

Batch022 row21049/stable1816057644940794 removes the player-name token imported
from the Spanish variant. Japanese/Chinese/English/German/French have no token;
the Spanish contract intentionally differs. Exact old pattern, Japanese source
tokens, source fingerprint and identity are pinned. All ten repairs are covered
by the existing looped idempotence/rejection/non-transfer tests, not a general
permission to harmonize locale tokens. Seabert21119 retains its current ordered
player/NPC tokens while using particle-safe vocatives.

Batch023 row18614/stable1794817603263553 and row18618/stable1794817603263559
remove Spanish-only player-name tokens absent from the Japanese slot and four
other locales. In18618 the fox has not arrived, so naming them as an addressee
while asking where they are also breaks the scene. Batch024 row18763/
stable1795328179342409 removes Spanish-only sw.Ninja contamination, restoring
the direct beverage name and original denial. These three bring the exact
allowlist to thirteen; all looped repair/rejection tests pass. No general parser
or cross-locale harmonization rule changed. Legitimate differing locale tokens
retained in reviewed Korean, such as19122, are not deleted without cause.

All snapshot groups prefixed `CH2A`, `CH3` and `DLG_` are now fully classified. This is
not whole-game completion or proof about related dialogue under other names.
Batch026 completes `Yohji_heart_4_2_2` (211) and `heart_4_2_2` (57):
268 rows, revised 46 / keep 222. Restore forced-holiday causality, Liliana's
painting versus Yohji's human research, older-sister kinship, master craftsman
Muramasa rather than personal mentor, living like humans, ambition's cost and
accountable apology. Restore fox-form confinement, priest Leon and Kuzuha names;
preserve friendship/romance/sister-refusal variants and legitimate locale tokens.
No new token exceptions or validation-code changes in Batch026.
Batch027 completes Yohji dates/sleepover/proposal/wedding: five groups188 rows,
revised41 / keep147. Restore wedding token contamination, human existence versus
customs, ruin referent, marriage-planning affection, mutual vows, half-pint
measurement/concession and arbitrary-name particle safety. Whole final Korean
reread against earlier heart arc; variants, games and callbacks preserved.
Exact row27131/stable1813236083654884 mixes start_wedding_npc+player+WeddingNPC
in old Korean. JA/ZH/EN/FR have player+WeddingNPC; DE/ES have player+start_wedding_npc.
Restore Japanese slot pair under exact fingerprint/identity/old-pattern checks;
fourteen allowlisted repairs now covered by all looped tests. Keep French-backed
player token27597 and legitimate Japanese wedding-vow player token27148.
Batch028 completes all157 Yui heart rows: revised34 / keep123. Restore family
disclosure ban, townspeople's emotional understanding, self-recognition, unknown
boy species, owned painting rather than invented authorship, shared-body inference,
answer versus clue state, body origin versus Yui's own identity, mayor title and
name-safe grammar. Keep gender/body source descriptions and hypotheses without
inventing consent, resurrection mechanics or confirmed dual spirits. No new token
exceptions in Batch028.
Batch029 completes Yui dates/sleepover/proposal/wedding:134 rows, revised41 /
keep93. Restore explicit departure25246 (historic hold resolved from full context),
comforting partner rather than leaning on them27265, ongoing civic work,
home/heart callback, project initiator versus operator, stress despite worthwhile
sibling care, childcare check, gender-neutral sibling-like-family teasing and
name-particle safety. Exact27253/stable1813235503409711 restores Japanese-only
start_wedding_npc from mixed three-token input. Fifteen exact repairs now tested;
not same token contract as Yohji27131.
Batch030 completes all134 Leon heart rows, revised39 / keep95, including appended
31326-31329. Restore class roles, uncertain human belief rather than proof,
mayor/title/name, fifth-generation ancestor estimate, book signing tour/Alin,
domestic warmth, partner autonomy and earlier offering vow now fulfilled.
Held23040/23078 resolved: spicy-stew affectionate nickname becomes heart-heating
metaphor instead of unintended Korean anatomical pun; no extra sexual content.
Distinct later dear-one variant preserved. No token-contract change.
Batch031 completes all170 Leon intimate rows, revised46 / keep124. Restore true
5/7/5 Korean haiku with mechanical syllable checks of nine lines, sorrow/hope and
playful alternatives; preserve poems' distinct keys. Keep deceased beloved's gender
unknown and first-marriage distinction; restore shared support vows, optional
reading/other-partner stories, crowd refusal, muse/autobiography and name particles.
No code or token-exception change.
Batch032 completes Liliana heart_4_2_4 (79), revised14 / keep65. Restore
painting welcome, older-sister relationship, hospitality rather than pickup,
affirmative gift reply, natural rescue surprise and name particles. Remove literal
surname before existing full_name token; canonical alias already has Shibata.
Keep Japanese/French/Spanish self-intro variant, not union with Chinese/English
late-departure text. No new token exception or in-game renderer test claimed.
Batch033 completes Liliana tavern/sleepover/proposal/wedding126: revised31 /
keep95. Restore sibling walk-in hope/uncertainty joke, cuddling referent, garden
flowers/first-meeting callback, voluntary all-night painting and improvised vows.
Keep childhood divorce/boarding memories subjective, not parental death or
present pregnancy. Name-safe grammar and family support restored.
Exact26633/stable1813236151020540 restores Japanese player+WeddingNPC pair
from mixed three-token Korean. JA/ZH/EN/FR/ES use the pair; DE player+start.
Sixteen exact repair identities were covered at that milestone; no broad
locale harmonization or parser change.
Batch034 completes five heart_4_2_4_5 through _9 groups143: revised36 / keep107.
Read overnight completion, flower exhibition/gift, teacher advice, personality,
sunset relationship alternatives, final art appraisal and private invitation.
Restore artist's individuality versus psychological personality/self-loss,
perfection versus mere completion, priest versus archer title, teacher respect,
flower addressee, lost confidence, name particles and cooked-fish callback.
Keep flower/dye terminology, friendship/romance branches and legitimate tags.
Full final Korean continuity reread completed before each merge. These ten
Liliana main/intimate groups348 do not include every daily/reaction line.
Batch035 completes Liliana101, Liliana-Reaction5 and Liliana's Room3:109 rows,
revised14 / keep95. Read birthday gift/leave and drawing/growing alternatives,
gift tiers, daily/seasonal/relationship reactions and all room inspection text.
Repair literal little-birthday-lunch/bottled-flowers/return-to-picture phrasing,
name particles, confidence encouragement, gradual-bloom simile and inspiration
wind versus weather. Restore source pearlescent glow; preserve mother's/Leon's
quoted notes, unopened gift state and valid locale-specific highlight tokens.
All109 final Korean rows reread before merge. These thirteen Liliana groups457
do not prove all her appearances inside other characters' groups are covered.
Batch036 completes BoneFireWelcome21: revised8 / keep13. Restore omitted smith's
community-development welcome, both siblings as guests, public-versus-whisper
distance, make-you-proud gratitude and name-safe grammar. Keep protection/weapon
and development/community replies separate, plus Korean call-and-response cheer.
All21 final Korean lines reread before merge. An earlier representative correction
is now covered by this full-scene review, not counted as a new approval again.
Batch037 completes six Ama heart/hot-spring/tavern/sleepover/proposal/wedding
groups146: revised36 / keep110. Restore reversed eviction agency, actress/role
versus designer identity, natural endearments/vows, name/farm particles and baby
class explanation. Localize speaking-my-language and one-in-a-million idioms;
keep deliberate landlord-roleplay theatricality and Ama's subjective Torleone
assessment. Legitimate locale tokens retained, no new exception. All146 final
Korean lines reread before merge. Older tone notes use 여텐구 while current map/
monster payload uses 뇨텐구; do not silently global-rename without final term QA.
Batch038 completes MissAmaText140:23 letters,94 content/46 keep-discard rows,
revised22 / keep118. Metadata Kon is reader/display role, not actual author.
Retain distinct supportive/hostile/concerned/colleague/shy/entitled writer voices,
letter boundaries and independent choice keys. Repair salutation-body distance,
biggest/number-one-fan calques, dress gratitude, notice-versus-recognize agency,
crush unawareness and emphatic reply demand. Korean Ama/dama/dara name rhyme
preserves silly fan verse; do not turn letter guesses about AI/scales/vampires/
counterfeit feathers or stalking pirate into world facts. Existing signatures,
movie titles and suspect fan descriptions stay. All140 final Korean lines read.
Batch039 completes Ama88 daily/birthday and Ama-Reaction6:94 rows,
revised23 / keep71. Distinguish tailoring-era gift first from actor-era many gifts,
consistent self-indulgent birthday refrain, criticism not dismemberment, stage
exit not physical direction, manicure/serenade wording, name particles and
burnout warning. Avoid literal parental claim in darling affection. Retain valid
localized2690 highlight difference, no token validator changes. All94 final
Korean lines reread before merge. Other Ama appearances still separate scope.
Batch040 completes Torleone_heart_4_2_6 (179): revised35 / keep144. Restore
chumming instead of water, former-boss reveal agency, Stormwave name, dream/
reality quote, dance-skill metaphor and celebrity-fixation concern subject.
Keep movie choices, quotations, confession to either adult, silence/engagement,
reflection requests and later engaged-couple/picnic variant distinct. Repair
seen-eyes/heard-conversation grammar, personal witnesses and name particles.
Seabert stays nephew/photographer; Kon's picnic inclusion not adult romance.
All179 final Korean lines reread before merge; no token exception added.
Batch041 reads149 new Torleone intimate rows plus179 heart rows again for
continuity:328 total, revised41 / keep287.39 new approvals and2 refinements,
not179 extra coverage. Restore five Stormwave names, first-mate endearment,
movie-to-sleep and own-roleplay meaning, hot-soak/settling idioms, name particles
and real-partner affirmation. Keep intentionally clumsy nervous marine vow,
crew absence/reply/gifts distinctions, fishing/love-luck joke and mild rod pun.
25359/60 omit Japanese-only animal labels absent from Chinese/English, restoring
primary-source traits without changing runtime edges or inventing zoology.
All328 final Korean rows read; earliest old_target preserved for refinements.
Batch042 rereads six proposal groups96: revised6 / keep90. Five new approvals
and one refinement18322, zero new coverage. Explicit player subject prevents
Kon being misread as dating spouse; invariant name particle preserves all keys.
Batch043 completes Torleone daily93/reaction7/room3:103 new rows, revised22 /
keep81. Repair collection quantifier, abundant catch versus large fish, morning
shop hours, first-mate term, sea idioms, gift reactions and missed-festival visit.
All103 final Korean rows reread before merge. Conditional schedules remain
separate; no runtime branches or extra relationships invented.
Batch044 completes Hephaestus heart_4_1_6 / _4 / Heart_4_1_6_5 / _6:
125 rows, revised44 / keep81. Restore Muramasa inscription request, protective
retirement argument, club departure, forge's first preview and primary quenching
tank, theft setup, combat-spirit idiom and ore-return conditional promise.
Gulubo warns inscription would disturb sealed magic, not confirmed existing curse
infection. Keep source-only name question/ellipsis without inventing translation.
Batch045 completes _7 / Heart_4_1_6_8 / _9 / _10:134 rows, revised31 / keep103.
Restore plural nightmare, uncertainty, consent question, pre-inscription blade,
forging exhaustion versus curse damage, willing alternative life-force bearer,
ritual performer/temporary effect, gratitude and completed-dream celebration.
Keep friendship/romance/curse-bearer/refusal options separate; do not rewrite
source's later smith decision into player-obedience. Existing vow warning21624
retains JA/EN offering-box reversibility, rather than stale Chinese irreversible
wording. No token exception added; all259 final Korean rows reread before merge.
Batch046 completes Heph hot-spring17/tavern24/sleepover40/proposal16/wedding61:
158 rows, revised34 / keep124. Restore player first-person proposal subject,
Kon's support subject and family-growth/class meaning, name-safe particles,
ol' Hephy self-address and smith's vows/muse imagery. Preserve sleepover dream
violence at Chinese/JA degree, no EN strangling escalation, no new family state.
Batch047 completes daily103/reaction5/room1:109 rows, revised22 / keep87.
Repair push-ups20 not sit-ups, indirect date hint, restorative sleep, forge/ore/
golem callbacks, name-safe greeting and birthday gratitude. Preserve conditional
schedules and source-supported list100 books/shield/new-muscle humor.
All267 final Korean rows reread before merge; no source token exception added.
Heph main reviewed scope totals16 groups526 rows, not every mixed quest utterance.
Batch048 completes heart_4_1_4 (166) and Nyo_heart_4_1_4 (26):192 rows,
revised46 / keep146. Restore polite drink acceptance21303 despite shared JA/EN
obedience calque, flight/training intent, long-term curse effects, magical
inscription not mere smith's name, emotional farewell/renewed life and consent.
Preserve temporary suppression not cure, friends/lovers alternatives and later
future possibility. Single catfish-god Namazu not two unrelated divine enemies.
All192 final Korean rows reread; no source-token exception or runtime changes.
Naming split found at batch048: NPC identity24/28 and55 payload rows used 여텐구;
map68/monster9 and15 rows used 뇨텐구. Selected scene retained current 여텐구. Final term
resolution must examine those occurrences and source/local identity evidence,
not blind replace or treat historical tone notes as sole authority. Research
originals remain unchanged. Candidate rows listed in POLISH_PROGRESS.md.
Batch049 completes Nyotengu hot-spring22/tavern28/sleepover27/proposal16/
wedding62:155 rows, revised25 / keep130. Restore jealous generous-heart sarcasm,
date-group threats, polite support and master teasing, Kon's preparation subject,
name-safe particles, ancestral greeting and renewed-life/domestic wedding vows.
Do not literalize resurrection or force curse permanently cured; source event
states and dialogue metaphor remain distinct. All155 final Korean rows reread.
Exact repair26839/stable1813236133572947: JA/ZH/EN/FR player+spouse, DE/ES
player+start-wedding, old Korean mixed3. Restore JA2 with known-pattern/source
guards, then17 exact token repairs. Parameterized tests cover these and unchanged
general token-loss rejection. Keep valid26854/66 rather than stylistic rewriting.
Batch050 completes Nyotengu daily109/reaction5/room4:118 rows, revised24/keep94.
Restore negative birthday-gift reaction, return-to-giver refusal, actual target
of jealousy threat, martial idioms and blade/drink qualities. Normalize selected
3861/62 to local NPC display 여텐구. At Batch050,57 occurrences used 여텐구 and13
use 뇨텐구; remaining mixed quest/map/monster occurrences need contextual review.
Batch051 completes Yoni heart46/hot-spring17/tavern16/sleepover30/proposal16/
wedding53:178 rows, revised26/keep152. Restore authentic musical self, performance
response, reciprocal confession, Kon household-support subject and wedding vows.
Gentle haeyo, music imagery and separate progression/refusal branches preserved.
No new token exception. All178 final Korean rows reread before merge.
Batch052 completes Yoni daily90/reaction8/room3:101 rows, revised21/keep80.
Restore lyric-polishing context, creative inspiration, unfinished song gift,
performance/birthday responses and natural affection/jealousy idioms. Preserve
legitimate JA/EN-supported variants and source-supported musical metaphors.
All101 final Korean rows reread before merge; exact token repair count remains17.
Batch053 completes7 numeric Yoni quest groups122 rows, revised22/keep100.
Read farm rehearsal, mentor/antler bargain and changing control, temporary
performance pause, Kon-only concern7, musical return/confession and band debut.
Restore jam intent, musical essence, exhaustion idiom and happy romantic assent.
Earlier heart sources overlap but separate occurrence keys remain independent.
Keep valid JA/EN bond-change mechanic31097 and direct kiss action31105.
Batch054 completes22 first-meet/garden/jam/material/ambient groups119 rows,
revised21/keep98. Restore father as referent for sleep-accompanying music28630,
completed delivery praise30282 instead of copied insufficient-material text,
dream advanced by helpers30283, settled-in timing and name-safe particles.
Preserve existing30283 JA location token while restoring primary/EN thanks.
First-meet sibling wording avoids forcing male player. Garden help5hours, seed
payment, postpone/refusal and material-completion branches remain independent.
All241 final Korean rows reread before merge; no source token exception added.
Batch055 completes9 wish-board/party/wedding-preparation groups39 rows,
revised13/keep26. Restore ema term, deepest wish, no writing-space observation,
first-of-many gifts, spell/allure and toast to Kon. No claimed objective magic
or newly multiplied romantic partners; wedding prerequisites/tomorrow/later intact.
Batch056 completes all135 TsukimiFestival_MoonKiss rows, revised18/keep117.
Preserve intentional mask persona changes, not force everyday voice into kappa,
feminine smith, Inari priest act or One-Eye hunter. Restore inverted Kincho
accountability-release polarity, missing prank-target warning, Yui compliment,
ritual terms and metaphors. Consent/refusal/exit choices remain independent.
Batch057 completes30 Carp-festival actors, revised8/keep22. Restore challenge
name, koinobori spelling, ready-for-games cue, future high-score boast, secret
hidden eggs and carp-as-ingredient recipe. Remove unsupported Koiwa mammals lore.
All204 final Korean rows reread before merge; no token exception added.
Batch058 completes Anna/Anji opening147 and third-eye60:207 rows,
revised22/keep185. Restore aid/visit intent, isolation reassurance, name-safe
grammar, third-eye possession/learning and spirit conversation. Repair22497
kill-him question copied from next reassurance; it is not an actual death.
Use pronoun22492 before reveal instead of prematurely naming Anji from differing
JA. Display-name Lightbulb spans override Anji metadata for actual speaking role.
Batch059 completes_7 (20),_8 (34),_9 (47),_10 (40):141 rows,
revised25/keep116. Include Anji-only intermediate20 missed by Anna-only inventory.
Restore Master Kuzuha, barrier responsibility, kiss-back action, reveal exit
option, omitted departure motives and unpack-before-discovery rather than wake-up.
Public identity speech's name particles, promise not to cause trouble and team
acceptance improved. Preserve legitimate JA sentence allocation/NPC token22553
alongside restored primary emotional content; no key or raw source remapping.
All348 final Korean rows reread before merge;17 exact token exceptions unchanged.
Current snapshot's groups containing explicit Yoni now all fully classified,
not a claim about aliases/blank speakers/non-AVG completeness. Anna main heart
scope is6 groups348 rows.
Batch060 completes hot-spring16/tavern39/sleepover30/proposal16/wedding67:
168 rows, revised28/keep140. Restore comfortable silence, uncertain prior
affection, feeling overlooked in groups, go-inside action and Kon's support role.
Lightbulb is the weird little spirit in the parent joke, not Kon. Restore actual
third-eye unlocking, Yokai Baby Class and completed apprenticeship callbacks.
Batch061 completes Anji daily98 and Anna-Reaction4:102 rows, revised12/keep90.
Repair morning greeting, omitted farmhouse-redecorating birthday choice, dating
and jealousy intent, staying up versus all night, and awkward work expressions.
Batch062 completes18 mixed numeric/quest/festival/casino/boss groups:66 rows,
revised10/keep56. Repair team invitation, public name particles, respected slime
transformation versus deity worship, wedding prerequisites and lantern collector
boast. Tales of Glory title is retained against approved glossary and book title.
All336 final Korean rows reread whole before merge;17 token exceptions unchanged.
Current snapshot groups with explicit Anna/Anji now all fully classified, not
aliases, blank speakers or non-AVG completeness. Continue remaining character
groups and separate UI/quest/book scope rather than counting speaker rows alone.
Count whole groups, not merely speaker rows.
Batch063 completes Musashi proposal16/wedding68:84 rows, revised22/keep62.
Restore Kon support subjects, family growth and separate/together class rules,
happiest-fox joke, double life, saved-life reassurance and wedding intimacy.
Normalize wedding26798 to NPC table24/28 spelling 여텐구 after full context;
58 current rows use 여텐구 and12 still use 뇨텐구. No global replacement performed.
Batch064 completes Musashi daily123/reaction5:128 rows, revised21/keep107.
Repair cat-nap/treat-myself/see-your-face idioms, afternoon choice, star-chart
wording, collaboration joke and natural spouse talk. Existing 고이노보리 checked
against approved festival references and retained, not arbitrarily respelled.
Batch065 completes13 mixed farm/home/shipping/party/magic/date groups:106 rows,
revised17/keep89. Restore guinea-pig meaning, Kon particle, next-day shipping
placement cue, awkward responses and outstanding wedding prerequisites.
Batch066 completes18 remaining mixed groups:78 rows, revised23/keep55.
Restore attack-to-cultivate instruction, green-thumbs skill, bag-expansion scope,
dango/tail boasts and8 repeated sincere greetings as natural spoken Korean.
Separate keys, optional upgrade/cost branches and potato shortage retained.
All396 final Korean rows reread before merge.
Batch067 completes mixed Shop52: revised15/keep37. Repair product honorification,
unknown item/amount suffixes, quantity/item confirmation and shady transaction
idioms. Preserve placeholder order, exact prices, annual stock versus daily stock,
no-credit and closure variants. Proxy player/system speech not blindly personalized.
All current groups with explicit Musashi now classified, not aliases/non-AVG.
Batch068 completes Yui Oda116/reaction6:122 rows, revised18/keep104. Restore
Kon-reported player decoration ownership, make-good versus repay, encouragement,
mayor title and home sentiment; improve rain/rest/gift-jealousy wording.
Batch069 completes Yohji daily87/reaction5:92 rows, revised18/keep74. Restore
research conviction, sleep/companionship idioms, diplomat jealousy, gift affection
and2 short poems as5/7/5 Korean. Full266 final Korean rows reread before merge.
Exact18th token repair27570/stable1795425752449203 removes malformed <i><I>... </i>
union to plain JA contract. Primary/EN/DE/FR have one valid italic pair; ES has
uppercase opener. Stable key/source fingerprint/known old tuple guards retained;
all18 covered by parameterized tests, no generic token validation relaxation.
Batch070 completes3 casino funding/seal/fog groups100 rows, revised29/keep71.
Restore Yohji's non-fox affiliation, seal handover condition, donation promise,
dark-fog safety and reopening instructions. Refusal/funding branches preserved.
Batch071 completes9 book/intro/ruins/15-pillars/Shuhei groups80 rows,
revised16/keep64. Restore visit purpose, conditional fog-clearing confidence,
painting clue and surname-first title; preserve valid localized variants.
Batch072 completes32 remaining mixed ruins/sister/marriage/friendship groups130,
revised21/keep109. Restore fox exploration-right subject, Liliana return referent,
acceptance condition, friendship scope and coffee-grinder pickup action.
All310 final Korean rows reread before merge; no new source-token exception.
The remaining explicit Yohji-containing group Uwabami&Alin_02 was subsequently
whole-read in Batch073. NPC detail88 surname/title conflict remains pending full
non-AVG source review; no blind string replacement performed.
Batch073 completes Uwabami&Alin_01/02 arrival and casino disappearance:135 rows,
revised22/keep113. Restore Kincho questioning Uwabami about missing Anna, own
departure instead of ordering Yui away, Alin's prince introduction, name/title
consistency, unknown-name particles and interview responsibility. Existing
source-backed malformed italic/shiver patterns retained, no new token exception.
Batch074 completes Uwabami&Alin_03/04 illness, vampire and ritual:146 rows,
revised19/keep127. Restore guilt about bringing Alin into miasma area rather than
Seikyu, family referent, regained self-control, offering prompts and gratitude.
Keep one-scroll sacrifice alternatives and merely inferred worldwide purification.
Batch075 completes Uwabami&Alin_05 shared confession:134 rows, revised21/keep113.
Restore both confessors' own feelings instead of commands to player, in-world
bond after either romance outcome, emotional referents/timing and bounty jobs.
Keep separate rejection/acceptance, valid JA/EN bond-change warning and token
variants. All415 final Korean rows reread whole before immediate merge.
Explicit Yohji-containing groups now all classified, not aliases/non-AVG.
Batch076 completes Uwabami hot-spring19/tavern20/sleepover34/proposal16/wedding59:
148 rows, revised19/keep129. Restore eastern hometown cue, design appreciation,
unknown-name particles, couple-separate/family-together class distinction and
natural vows/death callback. Exact27071/stable1813236111417799 repair restores
JA/ZH/EN/FR player+spouse, not union with DE/ES player+start-wedding tokens.
Nineteen exact repairs now tested, no generic source-token contract relaxation.
Batch077 completes Alin hot-spring26/tavern58/sleepover38/proposal16/wedding66:
204 rows, revised30/keep174. Repair Alin spelling, privacy versus introversion,
being asked a question versus asking it, Uwabami worrying about Alin rather than
Alin's own worry, class rules and literal intimacy/title phrasing. Stay-up choice
does not require all-night vigil. Preserve JA/EN26290 not-sleepy option even though
ZH says sleepy, plus existing source-backed token variants without new exception.
All352 final Korean rows reread whole before immediate merge and verification.
Batch078 completes Uwabami daily105/reaction4:109 rows, revised13/keep96.
Repair ambiguous boredom subject, forgotten-gift make-up promise, next-time tense,
unknown-name particles, game invitation and request-board reminder. Keep explicit
source game-style italic remembers-this joke4878, not an invented translator meme.
Batch079 completes Alin daily86/reaction3/room6:95 rows, revised13/keep82.
Repair prince title, privacy/gift/cooking phrasing, named umbrella plus other
familiars, effective daggers rather than skilled assassin, and circuit functionality.
Item1216 English-based 가사오바케 versus dialogue JA-based 카라카사 코조 was a
cross-surface followup at this checkpoint. Batch191 resolves it by reading the
actual item and dialogue references; no blind global rename was performed.
Batch080 completes30 remaining mixed groups85 rows, revised9/keep76, including
all32 Uozumi childhood/fishing/lost-home/family-support rows, both8-row wedding-date
flows, full Sasaki/Shuten shop quarrel and each independently keyed ambient group.
Repair separation-sacrifice idiom, unfinished preparation and invitation progress.
All289 final Korean rows reread before immediate merge; no new token exception.
Current explicit Alin/Uwabami-containing unclassified groups: zero, not a claim
about aliases/blank speakers/non-AVG or all script completion. Continue remaining
characters and common flows. Uozumi whole inventory not implied by32-row heart.
Batch081 completes the entire191-row Mika heart, revised25/keep166. Restore
explainer/comfort roles, involuntary travels and family selling her, safe belonging
and encouragement; retain source non-explicitness, uncertain recovery and branches.
Batch082 completes hot-spring17/tavern15/sleepover20:52 rows, revised13/keep39.
Repair compliment-blush versus shared-soaking choice/response alignment, overnight
party excitement and game/manga idioms without invented sexual subtext.
Batch083 completes planning16/wedding57:73 rows, revised19/keep54. Repair baby-class
term/separate attendance, unknown-name particles, mutual support, capybara/water
metaphor and literal hot-spring-access joke, plus finally feeling she belongs.
All316 final Korean rows reread whole before immediate merge. No new token repair;
existing EN-backed italic and JA-backed player-token variants retained.
Batch084 completes daily/birthday/gifts93 plus reactions4:97 rows, revised17/keep80.
Restore keeping-player apology, welcoming missing-presence idiom, explicit self-love,
Kon-only ghost belief, future event tense and arbitrary-name particles. Keep original
vulnerable self-blame viewpoint from aligned JA/EN, not an endorsement or new claim.
Batch085 completes25 mixed groups93 rows, revised19/keep74. Restore copied17682
worldview hope, predictable-game preparation, real-world bonds, ema term, reception
place, invitation progress and figurative game expertise. Displayed guard role is
not Mika/player proxy metadata; fine multiplier, insufficient-funds exception and
price remain exact. Whole190 final Korean reread before immediate merge, no new
token exception. Explicit Mika-containing unclassified groups now zero, not proof
of aliases/blank-speaker/non-AVG completeness. Continue other characters/common flows.
Batch086 completes Yuki Gulubo quest63 and garden19:82 rows, revised23/keep59.
Remove Japanese pronouns; repair Kon's knows-own-choice versus doesn't-know reversal,
kindness persuasion idiom, ice/thaw friendship pun, name particles and plot limits.
Both exaggerated freeze-to-death request and peaceful ice-cream alternative remain.
Batch087 completes restoration60: revised10/keep50. Restore Gulubo referent versus
fox visitors, Korean name, seeing inner person beyond snow form and reward as
snow-child form rather than restored human form. Refusal and later return remain.
Batch088 completes affection/friendship/form-rejection/first-kiss75: revised28/keep47.
Remove Japanese pronouns/alias, repair shallow-appearance accusation, icy rejection,
melting heart and mushy-affection calques. First kiss means after restored body,
not a first-ever lifetime kiss. Keep non-explicit bodily agency/refusal and separate
branches; JA/EN Inari-offering change-of-bond instruction retained over older ZH.
Whole217 final Korean reread before immediate merge; no new token exception.
Batch089 completes planning16/sleepover28/wedding61/hot-spring3/tavern4:112 rows,
revised33/keep79. Remove Japanese pronoun/ending residue, repair moist-atmosphere
calque, clan grievance settlement, emotional vows, unknown-name particles and
baby-class term/separate attendance. Retain abrasive warmth and public-date refusal
versus private invitation/boundaries and independently keyed visitor jealousy.
Batch090 completes daily/birthday78/reactions4/scheduling8/mixed greetings-report5:
95 rows, revised8/keep87. Repair broken hedged admission, name, liking-versus-anger
idiom, worthwhile rest and hypothetical jealousy threat rather than certain death.
Whole207 final Korean reread before immediate merge; no new source-token repair.
Explicit Yuki-onna-containing unclassified groups now zero, not aliases/blank speakers
or non-AVG completion. Tree name5097/5134 retained for later cross-surface lore audit.
Batch091 completes Sasaki daily/birthday/gifts115 plus reactions5:120 rows,
revised13/keep107. Restore emotional birthday significance, little-joys appreciation,
name particles, present favorite house, Maya-grandmother address, cooking/rest idioms.
Keep upgrade costs, next-morning visits and shop hours/closures exact.
Batch092 completes furniture-placement10/followup-identity38/material-letter24:
72 rows, revised9/keep63. Repair unclear decorating choice, Kon's credit/name particle,
guardian respect and identity wording. Answer to is-true-form-all explicitly says
not all; bare yes would reverse the primary/EN more-than-form affirmation.
Preserve early Seiryu belief rather than premature later identity revelation.
Whole192 final Korean reread before immediate merge; no new token exception.
Remaining Sasaki mixed quests/groups still require review.
Batch093 completes recovery/tree-identity48/bark1/first studio19/foxhole17:85 rows,
revised12/keep73. Restore missing identity answer and warmth of being needed,
Maya as only lead, source-generic mountain-tree reference without early explicit
identity insertion, permission/deal, sign-angle grammar and name particles.
Batch094 completes13 building/weapon/storage/furniture/materials/wedding/chess
groups76 rows, revised12/keep64. Match actual item701 construction kit and262
요괴 가마솥, clarify no-building-on-field and next-day sequence, any-owned-chest
access, injury check-in thanks, blacksmith referral and invitation progress.
Item-name lookup is narrow term evidence, not non-AVG full coverage. Loading-hint62
shortened cauldron term remains a later non-AVG check with other equipment names.
Whole161 final Korean reread before immediate merge; no new source-token exception.
Batch095 completes remaining22 Sasaki mixed groups64 rows, revised8/keep56.
Repair pre-repair cheer, home-heart effect, sibling housework retort/name particles,
full-belly interjection, bonfire downer idiom, BBQ praise and wish-board capacity.
Explicit Sasaki-containing unclassified groups now zero, not aliases/blank speakers
or non-AVG completeness.
Batch096 completes Uozumi daily/fishing/family/birthday58 rows, revised8/keep50.
Repair prank-instigator/name particles, edible fish context, item469 새우 주먹밥,
aging wings and natural family-missing phrasing; no bereavement invented.
Whole122 final Korean reread before immediate merge; no new source-token exception.
Batch097 completes remaining explicit Uozumi mixed groups: 19 groups/81 rows,
revised12/keep69. Clarify two mutually loving parents, three full nurturing seasons,
first marriage year, gender-neutral aunt-role phrasing and when-ready response.
Feast fish means eating more, not going fishing. All explicit Uozumi-containing
groups now classified, not aliases/non-AVG completeness.
Batch098 completes Prince daily/gifts/seasons/birthday63, revised7/keep56.
Restore row4097 from unrelated cat-form first-meeting love letter to Prince's
birthday help request, corroborated by all source locales and adjacent choices.
Repair20 is pinned to alone-table stable1806646314739610, exact contamination
tokens and canonical Japanese; cross-table identity rejection added to regression.
Fix land celebration versus on-water wording, Uozumi fishing host and literal
hot-blooded physiology. Whole144 final Korean reread before immediate merge.
Batch099 completes remaining explicit Prince mixed groups:22 groups/148 rows,
revised14/keep134. Read hooked-cucumber meeting, egg-hunt refusal/reconsideration,
full parent letter and homesickness/bench transformation, watering, festival,
mask and reaction branches. Restore parents' warm child address and trusted support,
gender-neutral newcomers and variable-name particles, visit-after-reverting order,
and own belief after player denial. Whole148 final Korean reread before merge.
No new token exception; explicit Prince-containing unclassified groups now zero,
not aliases/blank speakers/non-AVG completeness.
Batch100 Leon daily/gifts/seasons/birthday108:revised15/keep93. Restore more-perfect
romantic compliment, pepper-hot flirt, gifts-as-flirting, special birthday and
natural reading/rest advice. Row3428 weekday uses primary/English Tuesday rather
than differing JA Friday; runtime timetable not independently inspected.
Batch101 library pop quiz58 plus Fox Clan echoes28:revised18/keep68. Clarify
Namazu god-domain question and catfish-god answer, missing fox disappearance,
forgotten transformation role and remove Fox Clan equals all-yokai history insertion.
Keep15 chapters, rumored page owner, altar eligibility and suspicion unproven.
Batch102 remaining Leon mixed27 groups/132 rows:revised33/keep99. Restore Ama's
old-folks protest, human-form celebration, art-class one/two-person outcomes,
book-cover importance reason, ancestry-class invite, pepper meal and wedding
readiness, festival possession/goddess joke and fair offering reward.
Consistent polite teacher self-reference does not alter private author aside voice.
Whole326 final Korean reread before immediate merge, no new source-token exception.
Explicit Leon-containing unclassified groups now zero, not aliases/non-AVG proof.
Cross-surface pepper term remains followup:quest216/282 만티코어 versus daily3451
맨티코어. Narrow lookup is not full non-AVG review or permission for global replacement.
Batch103 Shuten daily/family/romance/birthday92:revised13/keep79. Fix variable-name
particles, overly mandatory advice, reciprocal family care and mixed-gender sibling
assumption. Source4510 gift polarity conflicts:Chinese negative, all five auxiliary
locales positive. Apply designated primary negative and record runtime trigger unverified.
Batch104 Kon illness/tree ritual/human-form party6 groups/86:revised21/keep65.
Restore Anna witness role, heading-out direction and welfare check, generic tree
references before optional Yamabiko reveal, roots and power origin, absorbing curses
without invented purification/destruction, symptom question and ritual item particles.
Fix Ritsuryo human-form liberation calque and late-appended player transformation
choices; no graph inferred from row order. Whole178 final Korean reread before merge.
No new token repair; other Shuten mixed groups remain incomplete.
Runtime followup:Leon3428 weekday and Shuten4510 gift reaction conflict with auxiliary
sources; current primary-based text is not proof of live NPC schedule or gift-affinity trigger.
Batch105 Kinn chef dream43 and Seabert photo exhibition24:revised9/keep58.
Restore chef appointment/celebration, photographer personality rather than literal
portrait, closing thanks for believing in him, scout role and named-subject particle.
Batch106 remaining Shuten24 groups/89:revised16/keep73. Fix behind-bar counter
versus tavern rear, excited/uncertain work choice, last photo to hang, newcomers'
variable-gender/particle and guardian intro, delighted やばい misread as distress.
Explicit Shuten-containing unclassified groups now zero, not aliases/non-AVG proof.
Batch107 Seabert daily/fishing/photos/work/birthday58:revised9/keep49. Correct
busy/unable-to-leave-work idiom, past festival question, gift as photo subject,
friendly drink word and birthday dinner/farewell. Other Seabert mixed groups remain.
Whole214 final Korean reread before immediate merge; no new source-token repair.
Batch108 Ritsuryo tabletop McDucky57:revised16/keep41. Restore Seabert not Ritsuryo
as newly brave actor, lost not spent money, guard actually knocked down, natural
staff roleplay and food/body-size joke; distinguish imaginary courage from real-life claim.
Batch109 remaining Seabert31 groups/174:revised25/keep149. Restore standalone
first-meeting29095 uniform/height worry duplicated from29100 encouragement in JA,
purchase affirmative misread as visited farm, dynamic-name particles, resemblance
callback, fishing/photo instruction, singer favor and camera loan-then-gift sequence.
Six-locale28876 conflicts:primary fishing greeting versus five auxiliary fish offer.
Current primary-based text is not proof of runtime bark trigger; followup playtest item.
Whole231 final Korean reread before immediate merge; no new token repair.
Explicit Seabert-containing unclassified groups now zero, not aliases/non-AVG proof.
Batch110 Yui community purpose/fox heritage/baking/request board:102 rows,
revised18/keep84. Correct variable particles, mayor's role in residents' independence,
heritage protection, swapped tutorial descriptions and invented local-only item restriction.
Keep egg/mayonnaise/sugar list: followup Chinese31202 independently corroborates it.
Batch111 audition dismissal/ingredient reminder/human form/town/combat tutorial:
57 rows,revised11/keep46. Restore visitors leaving rather than Yui leaving,
favorite-pastime callback, proximity cue and name particles. Close malformed bold20955
with one exact-identity/full-original-JA/pattern-pinned rule, separate from20 prior
source-contamination repairs; not a generic source token normalization policy.
Whole159 final Korean reread before immediate merge, no outside changes.
Batch112 Namazu food handover, welcome and Nyotengu apprentice:65 rows,
revised13/keep52. Restore Kincho's research plan/town priority, mayor logistics,
promising novice not already-best fighter, and weapon not iron will.
Batch113 true-form speech/hot spring/lighthouse/rest/baking:70 rows,
revised12/keep58. Restore Yui's own appearance in reassurance callback,
speech purpose, gender-neutral sibling greeting, collection quantities and natural dialogue.
Batch114 remaining52 explicit Yui-containing mixed groups:187 rows,
revised21/keep166. Festival speech, drink-giver suspicion, variable partner particles,
prospective one-year blessing durations not next-calendar-year copy, unsupported
goddess name and human body versus human species distinction corrected.
Whole322 final Korean reread before immediate merge. No new token exceptions.
Explicit Yui-containing unclassified groups now zero; aliases, blank-speaker related
content and non-AVG tables are not thereby complete. Blessing30129-30132 text follows
Chinese next-one-year duration; actual runtime activation/expiry remains unverified.
Batch115 all remaining explicit Koiwa mixed19 groups:169 rows,revised25/keep144.
Restore invariant name particles, pre-challenge state, animal care regularity,
raccoon species, ranch pet-product sales not home delivery and spell/charm function.
Koiwa3244 Chinese prayer-to-Inari versus Japanese/English gift-thanks conflict:
current auxiliary-localized gratitude retained; actual reaction trigger unverified.
Explicit Koiwa-containing unclassified groups now zero, not aliases/non-AVG proof.
Batch116 Hephaestus forge/shop advice/run/attack/ore7 groups:74 rows,
revised23/keep51. Restore helping actor, entrance location not decor, craft/customer
needs, player's steel-body compliment and smithing pun, suspicion not proof,
and still-seeking ore not already-found state. Other Hephaestus groups remain.
Whole243 final Korean reread before immediate merge. No new token exception.
Batch117 remaining Hephaestus32 mixed groups:128 rows,revised29/keep99.
Restore birthday material gift not future weapon, egg-team acceptance not gym invite,
optional fitness invitations and club stage, post-curse run request, party departure,
reciprocal body compliment and tool rather than weapons-only upgrade question.
Batch118 Fujiki10 whole groups:125 rows,revised19/keep106. Name/location particles,
variable-player sibling gender, lodging conditions, friendly apology not ominous
foretelling, scroll rival's not-over threat and first-of-many lover gifts corrected.
Whole253 final Korean reread before merge. Explicit Hephaestus/Fujiki unclassified
groups now zero, not aliases/blank-speaker/nonAVG completeness. No new token repair.
Scroll-info18546-18549 keeps informational voice despite Fujiki speaker metadata;
metadata is not independent proof of actual display/speaker runtime role.
Batch119 Tommy cookoff/family party/daily/birthday13 groups:155 rows,
revised15/keep140. Restore kinako ingredient, judge actor, already-cooked dish,
gender-neutral family and dry brotherly/death humor without adding facts.
Tommy4537 Chinese fish-reincarnation thought versus five auxiliary Hamlet-style
fishing questions: retain existing localized joke; actual trigger unverified.
Batch120 Ivan first meeting/transformation/work/daily/birthday13 groups:93 rows,
revised10/keep83. Restore warning addressee, reported dragon folklore, sake item
terminology and gifts improving the evening rather than arbitrary ramen ingredients.
Batch121 Theo love-letter/poem choices/stall/birthday/daily27 groups:144 rows,
revised16/keep128. Restore sarcastic wooing-versus-writing contrast, desire/distance,
regret poem choice, pending letter/proposal states and variable-name particles.
Theo30459 Chinese positive versus Japanese/English negative: retain contextual
sarcasm;30480 follows Chinese regret rather than Japanese romantic retry.
Raw row order is not runtime proof of poem-choice response edges.
Whole392 final Korean reread before immediate merge. No new token exceptions.
Explicit Tommy/Ivan/Theo groups were selected in full; aliases, blank-speaker
related content and nonAVG tables remain separate unfinished scope.
Batch122 remaining Liliana29 groups:188 rows,revised17/keep171.
Garden permission/paintings, ore acceptance/resume/delivery, Ephemera vigil/callback,
hot-spring flower choices, wedding preparations, Sasaki injury/care/furniture delivery,
first-meeting daydream and artistic self-expression corrected where needed.
Primary17542 peony taxonomy differs from JA; existing localized Korean retained.
Batch123 remaining Kinntarou30 groups:191 rows,revised26/keep165.
Restore mock psychological game-piece assessment, older-brother introduction,
eating-versus-thinking punchline, physical recovery, lemon request, cooking teacher,
gift-time idiom and birthday-menu actor/retort. Correct verified static NPC particles
separately from arbitrary player-name grammar. Narrow NPC-name lookup is not nonAVG coverage.
Whole379 final Korean reread before immediate merge; no new token exceptions.
Explicit Liliana/Kinntarou unclassified groups now zero; aliases/blank-speaker
related content and nonAVG tables remain unfinished.30545 burst pearls versus
auxiliary marble remains neutral Korean bead, not proof of material/edibility.
Food-coma hyperbole and source-level birthday gift offense retained, not sanitized.
Batch124 remaining Torleone41 groups:194 rows,revised28/keep166.
Fishing retention/tasting and reward-desire idiom, fish-size statement, work/wedding
preparation, film/favorite quote and conditional movie-night invitation corrected.
Reuse already-approved25420 film title 여인의 폭풍 for30597/30602, preserving
deliberately wrong30594. Separate player/Ama, player/Torleone and Torleone/Ama
romance resolutions; retain positive relationship support versus objection to
proposal approach, full current identity and slow-engagement condition.
Batch125 remaining Ritsuryo29 groups:114 rows,revised12/keep102.
Restore intelligent-not-luminous hero epithet, arbitrary/static name grammar,
wrong-flavor brother gift, stocked-soda delight, active secrets search and own-fur wish.
Keep child mock-warrior bravado and sincere father-search birthday, immediate/delayed
Sasaki-help choices, harmless localized barks and counterfactual combat boasts.
Whole308 final Korean reread before immediate merge. No new token exceptions.
Explicit Torleone/Ritsuryo unclassified groups now zero, not aliases/blank-speaker
related content/nonAVG completion. Narrow name/title lookups do not add coverage.
Batch126 remaining Miss Ama31 groups:197 rows,revised30/keep167.
Restore fan acknowledgment/emotional-ordeal/keep-chin-up/cutting-room-floor idioms,
Theo/Ritsuryo name outliers, hurt person's referent, sorting/work-observation action,
static/arbitrary name grammar, invitation preparations and uncertain love-story match.
17768 ZH/EN stay briefly versus JA leave-her-alone: follow primary limited stay,
runtime edge unverified. Keep comic vanity and treat hate-mail judgment as her viewpoint,
not proof all criticism is objectively malicious. Nickname/tailoring exaggeration retained.
Batch127 remaining Nyotengu25 groups:98 rows,revised14/keep84.
Clarify nearby harmful beasts, flight versus stumbling on ground, feather training power,
appearance-versus-ability idiom, invoking protector's name, modest feast invitation,
lethal equipment-independent warrior, trader warning and attack-opening combat tips.
Preserve stern/ritual/intimate distinction, graduation versus continuing apprentice bond,
source-strength violence and localized weapon metaphor; no new mechanic assertions.
SDTest/SDTest2 five JA-empty entries retained with canonical keys; repeated Latin test
strings in auxiliary languages do not authorize inventing Korean or deleting rows.
Whole295 final Korean reread before merge, no new token exception/outside change.
Explicit Miss Ama/Nyotengu unclassified groups now zero, not aliases/blank-speaker/nonAVG.
Mayor title31136 and prior 여텐구/뇨텐구 cross-surface followups remain for complete
related profile/quest/table comparison; no global replacement from a narrow lookup.
Batch128 remaining Kincho15 groups:130 rows,revised36/keep94. Restore invitation
versus furniture/house-extension states, romantic date versus scheduled date,
Uozumi reproduction class, clan referents, prayer speaker and twelve-egg quantity.
Reward inventory and schedules remain runtime checks, not proven by text review.
Batch129 Nine Lives/Mr Croaks10 groups:106 rows,revised9/keep97. Clarify merchant
referral, guarded-box warning, mind complaint, particle-independent item handover,
and princess letter's return request. Primary guarded-box text conflicts with
JA/EN safe phrasing; ownership remains the merchant's claim. Croaks30315 speaker
metadata differs from all-language player-like narration; retain narrative role.
Whole236 final Korean reread before immediate merges. No new token exception.
17858 was absent from the payload, not a Japanese translation entry: review viewer
fell back to original Japanese. Exact registered addition restores the taunt and
keeps identical17863 independently. Payload now22,532 rows, no deletes or remaps.
Explicit Kincho/Nine Lives/Mr Croaks groups now classified, not alias/nonAVG completion.
Batch130 ancestors/Kon forms, Yuki-history variants and parent-letter7 groups:
150 rows,revised40/keep110. Restore scroll protection versus claiming leader
subjugation, human-form walking practice, symptom relief versus curse cure,
player original-form constraint, Kon fox-form pride, power instability, continuing
Yamabiko protection, frozen crops/young foxes, snowman form and lost-self grievance.
Letter fragment location is under farmhouse; parents' residence remains inference,
departure remains intended, and sole inherited scrap carries emotional/evidence stakes.
Replace redundant foxhole synonym gloss with searching inside the holes.
Whole150 final Korean reread, then whole47-row illness group reread after refinement.
16346 retains compatible Japanese player counterargument/token while restoring
primary self-defense; no token exception or invented fact.16021 follows primary
cannot-model-form state over JA/EN repeated transformation observation.
No outside-batch changes. Other ancestor flows remain unfinished.
Batch131 remaining ancestor7 groups:201 rows,revised45/keep156. Whole source and
final Korean read; restore boar sprint/smash cue, beauty-sleep joke, last-letter
fragment state, parents as subjects of future discovery, clan/home lore, sensory
perception versus visual acuity, trial host/challenger distinction, Dark Fox ahead
versus past passage, exceptional control skill and Muramasa-built room.
Primary/EN kinship: Uncle is great-grandfather's younger brother, Grandma is
great-great-grandmother; Grandpa's generation stammer intentionally stays vague.
Grandma's peer reference avoids making player's Uncle her own uncle.
Exact repair21 removes31334 French-only player variable; no generic deletion.
All explicit Fox Ancestor-containing groups are classified, not all aliases/nonAVG.
Batch132 Gulubo introductions8 groups:87 rows,revised32/keep55. Ten Kenshi rows
were copied from adjacent rows:30365/67/68/71/72/75/76/77/78/79. Restore player
choices, Kon reaction, self-introduction, threatened scroll, training, combat
instructions, excitement and armor at each original identity. Never shift keys
or rotate a table globally. Correct nearby repeated occurrences stay independent.
Seven exact repairs22-28 strip mixed DE/EN/ZH/ES tokens to original JA contract:
30341/43/52/56/81,30401/09. No wildcard stripping; source/sequence checks stay.
Restore generic Transformation Scrolls versus Fox-specific reward, player-name
particles, gender-neutral Clan prophecy, Queen promises/contracts, trapped monsters
versus blanket safety, control-skill access and generic scroll uncertainty.
Kon uses light polite speech to titled Queen; peer teasing remains lively banmal.
Whole87 final Korean reread before immediate merge. Other Gulubo trials/minigames/
prince flows remained168 unfinished rows at132, not counted by name lookup;
133 below completes that packet.
Actual armor/sword rewards, charge controls, water breathing and flight remain
runtime checks; text review does not prove those mechanics execute.
Batch133 remaining Gulubo22 groups:168 rows,revised32/keep136. Whole source and
final Korean read including Prince initial/resumed quiz, blocked/hidden passages,
Queen hide-and-seek, agility/maze/invisible path/balance, final guardianship pact,
and cultural/tofu/barrel minigame wrong/retry/success alternatives.
Restore Kon/player fearlessness actor, Prince pending mother inquiry, passage
already revealed, caution behind door, preserved labyrinth, near-end progress,
ancestor knowledge sharing, same Fox Halls now in ruins, Duke name particles,
joint training request, readiness visit and Yohji never reaching Prince gate.
Tales of Glory1:4/2:1 uses primary/German chapter/verse, not JA volume/chapter.
Primary deity tribute is not invented universal oath. Quoted life-without-death
being hollow preserved; exact current italic/shiver envelopes retained.
17948/17950 mixed emphasis repairs29/30 restore plain Japanese token contracts.
Source conflicts pending runtime context:17432 treasure-location guidance versus
auxiliary shared-reward/open-path promise;16319 future mother inquiry versus
auxiliary already informed;29376 after-entry question versus five auxiliaries'
how-to-enter. Follow primary without claiming tested reward/gate behaviors.
17496 ambiguous Bobo pronoun stays ambiguous, not invented extra trial/learning.
All explicit Gulubo groups now classified; this does not complete aliases/nonAVG.
Batch134 remaining small named36 groups:100 rows,revised19/keep81. Full17 tourist
barks, pet variants/vocalizations, dealer rehearsal, Kababa funding/partnership/
refusal/seal/profit branches, daily/birthday/gifts and complete Nini13 read.
Restore soft-opening not grand opening, no short wait promise, VIP joke, Yokan
relationship not shy personality, Clan glory, seasonal profit share, location-name
grammar, accepted partnership farewell, reciprocal birthday wishes and casual chat.
Nini preserves explicitly player-labeled3805/3807, generic gentle register and
primary heavy-rain scope, not invented biography or current playable status.
Hara punctuation and dealer18552 JA-empty/Chinese-only debug-like body remain
source passthrough; actual reachability unverified, not automatically translated.
30058/30070 existing valid highlight/location sequences retained, no new repairs.
Whole100 final Korean reread before immediate merge. Remaining AVG now contains
only Kon/player/blank source labels, not proof aliases or their character content
are complete. Pet Ukyo/Kyoto, Shima/Tora metadata does not authorize renaming.
Batch135 completes heart_4_1_1, Murals, RelicClues and GameStartAvg:139 rows,
revised44/keep95. Restore reassurance, sibling compliment, finding fox kin for
parents' news, happiness even without transformation and height-boast choices.
Separate Kon banmal from quoted inscriptions and records. Restore book-as-guide,
shared prosperity, historical change and optimism; preserve her unreliable war
speculation rather than treating it as fact. Restore unfinished letter fragment,
name-independent particles, safe password ownership scope and research-record
balance/danger/uncertainty. Younger-grandfather-brother term is row-local, not a
global resolution of conflicting ancestor generations. All139 final Korean reread.

Batch136 completes Kon, Kon-Reaction and KonPetAdoption:99 rows,revised25/keep74.
Restore gender-neutral family affection, birthday timing/concern/boss-role joke,
lake destination and concrete snow-angel activity. Fix fixed name particles and
literal seasonal-task wording; keep appropriate independent barks and variants.
Pet purchase cue matches current item882 반려동물 보금자리; cuddling is not
specifically bed-sharing. Context-only nonAVG lookup is not counted as nonAVG
completion or edited. Existing valid highlighting remains, no new token repairs.
All99 final Korean reread. Both batches immediately merged69 exact revisions into
canonical TSV and regenerated payload, with no outside-batch changes.

Batch137 completes six foxhole/parent-letter/seal-choice/workshop-clue groups:
88 rows,revised19/keep69. Match letter excerpts to RelicClues, restore parental
wish agency, uncertain scrap recognition and ongoing search hope. Keep both
seal-protection/handover routes and intentionally uncertain ancestor generation.
Source-order adjacency is not runtime branch proof. All88 final Korean reread.

Batch138 completes six illness/memory/practice/rest groups:106 rows,revised21/
keep85. Restore ease of transformation rather than ease of all life, gender-neutral
gratitude, mutual support/promise, self-continuity and correct care recipient.
Explicit row15916 exception: Chinese says human form weakens Kon, whereas JA/EN
say current form makes her sick. Keep existing Korean, supported by Chinese25970
(unable to become human, serious illness, tree cure) and16155/16159 instructions.
Record this narrow continuity judgment, not a silent or global source override.
Preserve intimate fox-body memories, sleep variants and fears. All106 reread.

Batch139 completes four earthquake/Namazu-history/Umibozu-tribute groups:
102 rows,revised33/keep69. Distinguish Kuzunoha from Kuzuha, same Inari from an
accidental second deity, missing Kuzunoha from assumed death, and a mortal lover's
inferred lifespan. Restore tribute return condition, magical confinement, gradual
feral takeover, danger/waking/feeding conditions and food delivery offers. Fix
farm-name particles, Kon's quiet report/offer register, mayor title and awkward
deity wording. Keep his testimony and conjectures distinct from confirmed fact.
Sake term is context-only item592 lookup, not nonAVG review/edit. All102 reread.
All73 revisions from these296 rows immediately merged with no outside-batch changes.

Batch140 completes11 home/marriage/Yuki-field/relationship-shrine groups:
126 rows,revised42/keep84. Remove Japanese first-person residue from anonymous
Yuki while retaining proud voice and field-only permission. Restore direct partner
address, invitation preparation state, whispered ring reminder and marriage-only
romance restriction; fix runtime-name particles and clue certainty. Row30943 keeps
existing JA/EN offering exception despite Chinese irreversible warning, supported
by Chinese shrine3809/3819/3821/3823. Row3825 instead restores Chinese specific
already-married refusal, not duplicated auxiliary offering text. Empty-JA3812
stays source passthrough; no runtime relationship operation tested. All126 reread.

Batch141 completes13 hot-spring/date/music/drinking/foxhole-reminder groups:
106 rows,revised33/keep73. Restore solo date departure, help into bed, drunken
speech, possible date anger, next-day closing cue, ticket/refund wording, sibling
banter and storage-container description. Exact17688/stable1804899039517200 is
excited acceptance in all six locales but had two copied player-name variables.
Repair31 removes only this exact old pattern to token-free source; new test rejects
one/three copied tokens, existing parameterized tests cover altered source/target/
identity and idempotence. Normal token preservation remains strict. All106 reread.

Batch142 completes12 room/sign/ruin/storage/shrine/divination/fan-letter groups:
90 rows,revised31/keep59. Restore expected stone weight result tiers, missing sign
headings, harvest/weather lore, right eye, model weapons, observed armor and storage
action. Keep the letter author's presumptuous future marriage/travel claims as
claims, not facts or the reader's voice. Tree sign does not add unproven Yamabiko
identity;5097/5134 and nonAVG cross-surface tree resolution remain pending.
Chinese-only debug-like23896/empty JA remains passthrough; radio-family lookup
is contextual, not new reviewed coverage or a global rename. All90 reread.
All106 corrections from322 rows immediately merged into canonical TSV/payload.

Batch143 completes11 ruin/trial/black-fox/bench/monster groups:104 rows,
revised15/keep89. Five readable monster bubbles18200-18204 were absent from
payload: register their exact source identities/fingerprints and original JA,
then approve Korean in TSV. Registry now6 rows, generated payload22,537.
Restore casino-box negative answer, free-food joke and rescue destination.
Choice30901 is the player's first-person recollection in Chinese/EN/DE/FR/ES;
JA alone has a spurious player-name vocative. Separate exact original-token
repair requires full unchanged JA/ZH/EN at stable1820218594496168 and existing
source fingerprint guard, permitting only the audited token pattern. Three
new tests cover idempotence, altered source/token rejection and identity isolation.
Dark Fox speaker labels override Kon metadata; nightmares and name-only rows
are not treated as missing translations. All104 final Korean rows reread.

Batch144 completes6 cooking/gift/noise/cake/mask groups:47 rows,
revised14/keep33. Restore wakeup/no-smell branches, gift-wrapping joke and
natural name-placeholder particles. Reuse actual item labels 날고기 and
숯불 꼬치구이. Mask30114 JA Red Oni conflicts with Chinese/EN Tengu and
item549/1294/clothing60/67 Tengu Mask: use 텐구; actual reward rendering
remains a runtime follow-up, not verified by name-table lookup. All47 reread.

Batch145 completes8 livestock/Muramasa/Gulubo/route/Yui groups:37 rows,
revised14/keep23. Restore Hephi as blade maker whom player helps, possible
curse-lifting purpose, master's pride, fluffy animals and prompt concern for
Yui.30362 had unrelated fox-clan recognition copied into a merchant-cat reply;
restore business-acumen/exploration dialogue.30531 variable-only name remains
passthrough. All37 reread. These188 rows produce43 immediately merged changes.

Batch146 completes35 common/room/bubble/settings groups:68 rows,
revised28/keep40. Six more readable monster lines18197-18199/18205-18207
were absent: exact registered additions now12, payload22,543. Restore
Musashi's whole letter, figurative father qualification and mercy ending,
Maya's affectionate note, observed room details and Mika letter's primary
opening-inquiry content, not auxiliary ownership-transfer assertion.
Bar18497 is32nd exact target-token repair. Chinese-only/empty-JA scarecrow
and placeholder Monster source remain passthrough, not invented Japanese text.
All68 final Korean rows reread.

Batch147 completes53 short quest/delivery/festival groups:120 rows,
revised26/keep94. Retain independently checked repetitive delivery branches.
Restore gifting particles, player routes, Inari's offering-care acknowledgment,
mask acquisition without added purchase requirement, eggs required for entry,
and Kon den furnishing.16557 malformed original </ishiver> receives a second
exact original-markup repair.29630 is33rd target-token repair. Added regression
coverage checks every original-markup repair's source/old/target/identity and
idempotence; existing bold fixture uses its explicit key. All120 reread.

Batch148 completes125 whole singleton groups:125 rows,revised28/keep97.
Restore active love-and-loss proverb, dawn singer, availability for coffee,
chess challenge, fire spread, mental clarity and possible location knowledge.
29475 receives third exact original-markup repair;30154 receives34th exact
target-token repair. Eight DateTest InteractionTitle literals Test_Lover are
identical in all six locales: exact eight identity/fingerprint/source/surface/
DateTest-prefix contracts preserve them, with regression rejecting any change.
No generic English-word exemption or runtime-unreachability claim. Empty-JA
family dinner labels and variable-only speech remain original passthrough.
All125 final Korean rows reread. All313 rows yield82 immediately merged changes.

Batch149 reads complete NPC names89/aliases8/profiles32:129 rows,
revised18/keep111. Correct Sasaki carpenter typo 대공, surname order 시바타 요지,
Mayor 오다 유이 matching approved self-introductions, and natural profiles.
Gulubo rank becomes 낭인; Uwabami's personal epithet 방랑하는 로닌 stays distinct.
Maya's absent-guardian wording does not invent irreversible soul death from
conflicting source wording. All129 final Korean rows reread, then immediately
merged into canonical TSV/payload.

Batch150 rereads255 previously reviewed Korean rows in CH2B_Q2.13 and Yuki,
plus targeted primary/JA/EN source around5 naming changes:revised5/keep250.
Correct19233 to NPC-matched 굴루보 낭인 and19316/19326/5097/5134 to 산신의 나무,
not an unproven personal Yamabiko identification. Prior whole multilingual
reviews014/090 remain historical evidence;255 reread adds no unique coverage.

Batch151 reads complete map57/location50/shrine5/monster-name34/empty-desc31:
177 rows,revised5/keep172. Align Nyotengu boss9/home68 to 여텐구,
Farmhouse shrine6 to 농장집, and Torleone fish-and-tackle labels in both fields.
31 monster descriptions are all-language empty, not missing invented lore.
Keep Theo+Ivan house name52 despite JA-alone Tommy+Ivan mismatch.
All177 final Korean rows reread. NonAVG map/tree labels independently support
산신의 나무; this does not settle the tree deity's actual personal identity.

The generic merge tool now selects either whole AVG scenes or whole non-AVG
snapshot tables; nonAVG decision refs are table:row-id to prevent collisions.
Four added tests reject missing/partial/duplicate/mixed groups and preserve AVG
behavior. The verifier separates AVG and nonAVG counters and checks every
classified identity/group/source excerpt against snapshot. The first55 legacy
classification records have no source columns: preserve their exact frozen
file SHA263eaf7a...1a9b01; all later receipts require full JA/ZH/EN excerpts.
Historical research/worksets and the original payload baseline are untouched.

AVG unclassified: 0 (first scene-by-scene pass only);
non-AVG unclassified:3,339 of5,250 (1,911 reviewed).
Remaining rows: i18n_custom1105, quest_default469 of590, item names883,
item descriptions875 and structural-schema follow-up interest_info7. Counts
retain all23500 original rows including empty slots, not just translated payload.
Full project is NOT complete. Non-AVG names/quests/items/books/UI and known
cross-surface terminology follow-ups remain, including10 Nyotengu variants
(five dialogue and five quest rows). Tree5097/5134 and NPC profile88 were
resolved in150/149; other explicit Yamabiko mentions are not automatically
wrong and must be checked against their own sources. First-pass scene coverage is not final global consistency,
runtime, rendering, schedule or trigger verification.
No CH2B_Q2.11/2.12 groups exist in the current snapshot; do not invent them.

Evidence is under the game data directory:
`translation_research/quality_audit_20261023/`. See `polish_validation.json`,
`polish_classifications.json`, `polish_state.json`, `polished_scene_readback.txt`, and
`POLISH_PROGRESS.md`.

Batch152: complete17 book titles,53 main titles and63 bodies, revised37/keep96.
Fixed parent-letter unknown-name particles and future wishes, mayor terminology,
tree labels, knowledge/conquest calques, famed versus infamous fireworks,
catfish king, conditional restoration of one specific transformation and exact
source-tag contamination in research report86. Retained all three cipher blocks
in51 byte-for-byte, tested independently, and aligned its readable counterpart74.
Preserve source correlation contradiction33, author bias, rumors and the396-volume
joke; do not modernize lore. Cipher50 unchanged. The stale pending66 note in the
batch manifest is superseded by its actual same-batch revision and receipt.

Batch153: complete213 rows in birthday/invitation/shared quest/bulletin/festival
tables, revised35/keep178. Read entire letter subjects/bodies/signoffs and paired
request headings/descriptions. Restore date venue, missed-appointment joke,
making-amends/candor idioms, hunter pursuit threat, prince title and festival
name/venue. Remove unknown-name fixed particle via explicit target label while
preserving exact token order. Same shared objective cannot assume a paper reply.

Batch154: complete109 rows across12 menu/shop/calendar tables, revised20/keep89.
Align Nine Lives merchant labels to approved 쿠조, fish-and-tackle storefront,
Korean inventory categories and Jump alias verified against actual custom1601/
prompt133 sources. Added3 exact original-literal passthroughs (Steam Deck preset,
two OK labels) with all-six-locale/identity/schema/fingerprint guards and mutation
test; no blanket English/ASCII exemption. Empty JA shop-category/camera fields
remain original passthrough, not invented translated rows or proven unreachable.
Inventory English may have been a font workaround: Korean strings require actual
bag category glyph-rendering verification before release, not just font references.

Batch155: entire102 transformation names/background/skills plus38 tutorial rows,
revised39/keep101. Restore primary form biographies without merging incompatible
JA-only migration/warrior-soul history. Restore small/elite taming eligibility,
non-recon stealth exception, directional absorption, capacity tiers, form-specific
blocking, and cooking auto-record versus switch-to-menu semantics. Source locale
disagreements in press/hold and freeze radius documented; runtime verification
is still required, not claimed by textual QA.

Batch156:49 new loading/buff/night rows, plus47 already-reviewed skill rows
reread for continuity; revised15/keep81, twelve new approvals and three refinements.
Complete buff table distinguishes primary耐力/Endurance from体力/Energy; refine
monster control87/88/89 to 에너지. The limited custom Energy alias cited in155
was not sufficient evidence to collapse pools. Preserve earliest old_target and
historical receipts rather than hide this correction. Restore Mountain Goddess
Tree hint70 whose JA described a different tree, rare bamboo cue65, Mayor title,
Inari provenance, Pearl Lake miracle traces, and event/flag terminology.
Dye tutorial7/12 source item-ID conflicts were not guessed away at156. Follow-up202
verifies original item links and resolves12 to Universal Dye25125. Preserve7's
split stations on actual equipment-body evidence. Custom labels reviewed192-197.

Batch157:124 complete husbandry/pet/life-skill/reputation rows, revised3/keep121.
Sale wording avoids unknown-animal-name fixed particle and preserves literal Y/X
count/order; distinguish unnamed versus unknown reputation and crowding versus
later no-seats rung. Keep65 proper pet names and all wild Gulubo occurrences,
age/moon/house/mood states without gratuitous renaming or stage-duration guesses.

Batch158:74 complete action prompts, revised3/keep71. Clarify water surfacing,
return item to backpack (not back navigation) and Farmhouse versus whole farm
renaming. Three additional OK labels preserved via exact source contracts, bringing
table-literal contracts to six. All covered by existing full-field mutation test.
Seven inspected interest_info rows appear structural: JA ui_livinglevel_frame_*
and EN localization paths, not dialogue. Still unclassified pending original-schema
corroboration, inside full23500 scope; do not inject Korean into possible asset IDs.

Batch159:133 whole shrine/portal/furniture/outfit/standard-word/report rows,
revised4/keep129. Restore generic Mountain Goddess offering label, goods without
unsupported luxury-quality restriction, and 侍神 as shrine attendant's garment,
not corpse 시신. Existing localized outfit proper labels kept without guessing
visual designs; standard resource words independently confirm156 distinction.

Batch160:127 complete crafting/cooking/item-category rows, revised3/keep124.
Food Dishes is food, not tableware; Haberdashery means sewing supplies, not
unrestricted miscellaneous goods. Same inventory source label unified to 가방.
46 primary-only cooking category rows retain blank JA/EN, not new translations.

Batch161:382 complete Synthetic Mix category occurrences inspected via exact
text groups with every occurrence ID and whole-table empty-locale assertions:
266 ZH/JA/EN empty,116 Chinese-only across16 categories. Every JA/EN/DE/FR/ES
field empty, no Korean payload entries. Zero revisions, unchanged payload and
approval hashes. These382 are verified source-slot absence, NOT translated Korean,
and do not prove runtime locale fallback absent. No deduplication/scope reduction.

Batch162:55 complete opening quest story rows including50 main and5 child
hand-in interactions, revised15/keep40. Correct welcome venue title versus
Inari Temple8pm description, stone gathering cue, fixed-name particles,
farmhouse-underneath foxhole clue, and mystery paper note distinct from parents'
torn letter. Preserve opening7pm versus welcome8pm and exact imported tokens.

Batch163:66 complete CH2A/CH2B and child delivery flows, revised10/keep56.
Correct Nyotengu, hot request/food praise, Kon as form-showing subject, and
Namazu surface-quake/continuous supply cause. Quest140 split is resolved with
CURRENT CHINESE dialogue18727/18740/18743/18746/18748 and title139: crafting a
piece precedes Secret Base access and speaking to npc4609. Keep JA/current KO
for that exact body, not blind override by majority or swapped NPC tokens.

Context flow selection uses explicit complete textasset/story_id pairs, separate
from AVG/full-table mode; three regression tests cover all-surface selection,
missing/partial/duplicate/mixed/wrong-schema rejection. Receipts retain table
group, verifier only completes table after ALL590 source identities covered.
590 quest rows reviewed:410 named narrative rows plus180 verified all-field-empty
original occurrences. No untranslated prose hidden by empty-story classification.

Batch164:49 CH3/trials/workshop/festival rows, revised14/keep35. Restore trial
completion, waterfall behind farmhouse, tentative claims and optional restitution,
personal Dark Fox offering and festival rice plants/sake preparation.
Batch165:52 Yui/Nyotengu/wedding rows, revised10/keep42. Correct missing-mayor
concern, Kon particle, filming invitation, guilt and four quest name variants.
Missing delivery choice556 registered with exact context fingerprint and JA.
All19 separate wedding deliveries retained. Payload22,544 rows/additions13.

Batch166:48 complete smith/Musashi/Liliana quest occurrences, revised12/keep36.
Restore fountain instead of spring, first encounter clue, life debt stakes,
actual item name 남동석, correct fixed-name particles and journal invitation role.
Original biography87 corroborates older-sister relation against isolated conflicting
quest14 older-brother claim; do not spread that contradiction. Missing delivery562
registered as14th exact addition. Payload22,545 original identities plus overlays.

Batch167:56 complete neighbors/tavern/hot-spring quest rows, revised16/keep40.
Restore Kon as co-invitee, tonight heist timing, farmhouse location, chopping
injury, messenger attribution and ritual-ready prose. Fishing invitation follows
primary technique/expertise rather than auxiliary-only new bait item claim.

Batch168:84 remaining named quest-flow rows, revised17/keep67. Truncated207/208
reread in full. Correct fixed-name particles, water fear, animal purchase versus
sale, current item108 보보 진주, recipient direction, farmhouse garden and tonight
meeting. Hand-in274 uses player-to-Ama polite register consistent with272.
At168 all410 named-story quest rows classified;180 empty-story rows still pending.
Batch169 then explicitly asserted every source/identity/context field empty for all
180 original rows and enumerated all row IDs. Previous410 source triples and final
Korean revalidated against162-168 receipts/current payload. Full590 table closure
adds180 unique coverage, zero new approvals or changed payload bytes. These are
verified empty original slots, not180 translated sentences. All identities retained.

Batch170:151 original weapon/armor/accessory name-description occurrences,
revised34/keep117. Restore toy-like training sword polarity, Wanyudo harvesting
souls versus souls composing flames, giant spiritual-power armor origin, crafting
blessing legend, strategist role and Kinntarou spelling. Japanese proper name
Hyakkimaru transliterated instead of Korean Hanja reading; no external lore added.
Source43 hat-name/cloak-body conflict retained for visual follow-up, not guessed.

Batch171:134 resource/pearl/dye occurrences, revised16/keep116/hold2. Restore
pond habitat, specific hardwood/resin facility uses, pearl shape/speculation,
wood processing, harvest processing and shared 잉어 축제 terminology. Dye134
initially held due to green/blue language conflict, not silently kept as verified.
Batch172 resolved both holds by original dye_palette602-byte full parsing and
exact item_item localized-key/item-ID correlation for all13 dyes:134 maps25119
channels118/145/100 (muted green),135 maps25120 channels0/82/67 (darker green).
134 name/body now 연녹색 염료. Material remains azurite; no inferred material swap.
Evidence: inspect_dye_palette.py and dye_palette_source_evidence.json in audit.
RGB interpretation corroborated by source pink/yellow/dark-blue anchors; no
claim of visual shader/gameplay test. Dye holds resolved; later174 has one separate
original-data hold. Historical hold decisions remain preserved.

Exact keyed-row manifest mode added for coherent item cohorts; three tests
reject changed/missing/malformed/duplicate/mixed/wrong-schema selections.
Partial receipts do not complete a table until every original identity is covered.

Batch173:214 crop/seed/basic-food occurrences, revised74/keep140. Restore
harvest/seed names, same-type allowed two-portion recipes, HP versus energy,
repeat-harvest and possible seed purchase. Root roast430 no longer narrowed to
sweet potato, toon/egg dish434 no longer generic scrambled eggs. Explanatory
item narrator register aligned with earlier inventory prose; original humor kept.
Source images in538/539 retained without pretending Korean 붓꽃/몬스테라 names
mean Chinese bird/turtle expressions. Raspberry crop/seed naming aligned.

inspect_item_links.py independently reads exact original length-prefixed name
and following description keys for876 referenced names. Names/descriptions often
have different source row numbers: e.g. celery150 -> body515, raspberry168 ->526,
seed209 ->551. Cohort expanded to80 extra real-linked occurrences, including
separate giant names/shared descriptions. Seven unreferenced source names not
removed or implicitly reviewed. Evidence item_links_source_evidence.json.

Batch174:62 new equipment/storage/consumable occurrences plus185/186 rereads,
revised19/keep44/hold1. Eighteen new approved identities and one refinement185;
earliest old target preserved. Fix workbench versus crafting material, monster-only
cauldron scope, sake processing, rice milling, exact machine labels,21 storage
SLOTS instead of21 total items, and collect fish rather than ambiguously retrieve
trap. Same-key duplicate cauldron/brewer prose matched without deleting identities.

Hold description977: source Koban name251 links to coffee-machine description
in all original locales; record uses item29003 and food-looking icon_item_29002.
Actual icon extracted read-only and inspected, but does not identify a definitive
replacement. No fabricated currency/coffee rewrite. See SOURCE_DATA_ISSUES.md
and item_251_source_icon.png. Further source/prefab/use inspection needed.

Batch175:116 new linked furniture/lighting/home occurrences, revised46/keep70.
Restore functional versus decorative claims, full-length mirror/stool distinctions,
modest/luxury contrasts, source jokes and shared polite inventory narration.
Koinobori pole agrees with actual flag names and carp festival terminology.
Source-only tribe459 is transliterated as 룽룽족; pronunciation remains a follow-up.
Exact source duplicates stay separately recorded; prior original-data hold977 remains.

Batch176:101 full linked ornament/fish occurrences, revised26/keep75; mirrors435/474
are prior175 rereads, so unique new coverage99. Fix wall ornament/pegboard/cabinet
identities, solid wood versus log, forgery versus neutral replica, original inscription,
and wry cultured-pretense joke. Localize ayu's year-fish nickname without salmon confusion.
Primary naming evidence and limited conflict decisions are in FISH_NAME_EVIDENCE.md.
Rainbow trout398 night follows primary text plus original fish42026 time bucket3,
corroborated against several day/night anchors in fish_times_source_evidence.json.
This is static configuration evidence, not a live catch/UI test. Other authored fictional
ecology stays intact; no speculative exact species assignment or source row removal.

Batch177:57 new linked fish/husbandry/food rows, revised24/keep33. Restore actual
chicken/crested ibis and dairy cow/goat occupants instead of chicks/cattle-only;
same straw resource112 throughout silo, and dumplings in chicken broth rather
than meatballs. Restore ice-clam pearl material and group-hunting joke. Distinct
old occurrences905/908/1449/1452 preserved, shared inventory narration polished.

Batch178:15 linked kappa identities, revised10/keep5;3 new coverage,12 rereads.
Five new approvals and five existing refinements. Align 갓파 with reviewed NPC
identity, ring/necklace/keepsake/cucumber/seed callbacks, and Tsukimi with 달맞이 축제.
Restore primary mask narrator's rebuke against ugly-kappa stereotype, not endorse it.
Original Gold5 and Kappa Cucumber408 also share blade descriptions1449/1452;
SOURCE_DATA_ISSUES.md records source wiring/placeholder uncertainty, not a license
to invent new objects or edit original references. Prior hold977 remains separate.

Batch179:73 new outfit/food/processor rows, revised45/keep28. Restore primary uniform
versus three whole robes, three armor pieces, fox-yokai relationship and completed
mission before armor sealing; remove auxiliary invented waiting-for-fated-owner.
Correct cassava pudding NOT being a tapioca substitute, moderate versus excessive
sugar, food versus recipe, beef/family stew continuity, and mortar versus grain mill.
Match exact reviewed outfit set titles and resource603 Energy/에너지.
Batch180:4 continuity rereads, revised1/keep3, no new coverage/approved identity.
Smooth book597 possessive wording; retain generic活力 and精力 as 활력 rather than
blindly force every invigorating-food sentence into exact体力/Energy stat label.

Batch181:73 new weapon/art/mask/food occurrences, revised40/keep33. Restore poisonous
man-eating flower source, priest/non-priest distinction, water/fire deity powers,
cheap replica and believed-divine victory rather than unqualified invincibility.
Preserve Liliana informal painting quote and dialogue22088 localized peony title,
contrasting fleeting flowers and painting callbacks. Restore playful mountain spirit
food/character, exact festival label, garment parts versus three whole outfits.

Batch182:45 new mask/husbandry/fishing/dango/crossover rows, revised23/keep22.
Restore value question rather than guaranteed price, doubtful real-gold joke,
slight wound-recovery dango effect, and actual label598마페이페이 versus body마피피.
Keep neutral vitality distinct from a numeric Energy stat. Restore greedy duo and
underdog punchlines instead of generic fortune/success promises. Crossover proper
names come from original item records, not guessed outside lore.

Batch183:44 parent-clue/reward/outfit occurrences, revised20/keep24;42 new,2 reread.
Restore fox seal's tentative parental origin and ruins mystery rather than certain
sealed-heirloom story; restore fragment collection/assembly and already-restored
full letter. Personal player clues stay first-person plain narration, distinct from
polite equipment narrator or quoted weapon threat. Match contest ticket to reviewed
challenge name, fake bait to entry prop, and plush636 to actual named Kon.
Restore original Twitch/Kickstarter limitations and armor versus black-flame object;
these historical original-item labels are NOT proof of currently active campaigns.

Batch184:56 new home/animal-material/treat/boardgame occurrences, revised31/keep25.
Fix hot springs incorrectly described as edible treats, hard one-treat-per-day limit,
raw manure676 versus finished fertilizer, and actual tea table653 versus tea-cup set.
Restore lyrical quoted fan/table/kimono prose and precise source crafting materials;
do not infer guaranteed animal friendship or measured feeding effects.

Batch185:70 kit/forage/coffee occurrences, revised39/keep31;67 new,3 rereads.
Restore exact construction transitions,4/8/12 occupants and coop-only incubation nests;
preserve compatible original auxiliary next-morning assistance timing without claiming
engine timing tested. Restore all-season foraging, blue sparks, cool spun silk,
actual cloud-lotus label and generic mountain-goddess tree instead of invented Yamabiko.
Coffee739 is explicitly coffee machine in all three sources and uses description977's
exact original key at item_item offset146912. This disambiguates the intended text
and resolves its TRANSLATION hold, NOT coin251's same-key wiring/icon source defect.
The original coin label and source references stay unchanged; see SOURCE_DATA_ISSUES.md.

Batch186:29 new furniture/display/den rows, revised17/keep12. Fix limited capybara
shelters versus auxiliary unlimited-sanctuary claim, garment parts versus whole sets,
straw-mat target versus straw doll, and actual armor/vase/fridge identities. Respect
769/770 primary absence of768's explicit Twitch limitation, not blanket promotion copy.

Batch187:85 material/pet-decoration/furniture occurrences, revised47/keep38;
82 new identities,3 outfit rereads. Original Japanese982 copied felt988 despite
actual OilWick812 and primary/English boss-drop/fire caution; Japanese989 copied
the wick description despite actual FruitWine819 and primary/English fruit wine.
Restore correct semantic sources without editing original slots or shifting rows;
source contamination evidence recorded in SOURCE_DATA_ISSUES.md. Align actual
ice-cocoon/cloud-lotus ingredients, grass rope material, and pet accessory roles.
Paper globe849 is a sphere, not Earth-map globe; primary1030 simile is moon not sun;
plate842 is flower-shaped, not necessarily a printed floral pattern.

Batch188:67 new console/art/pet-trust/seasonal occurrences, revised35/keep32.
Restore flute's sufficient-trust prerequisite, chess focus on next decision not
winning/losing, and primary kitten lying/playing versus Japanese running pose.
Preserve original gaming-device tactile/nostalgic details without invented bundled
game count. Restore hidden note versus full letter, original Christmas adornments
versus extra equip steps, and primary artwork metaphors. No measured gameplay
effects or actual model/canvas display claimed; valid title variants left intact.

Batch189:146 fishing/trap/fertilizer/taming/giant-crop occurrences, revised52/keep94;
116 new identities,30 rereads. Fifty-one new approvals and refinement526; earliest
old Korean preserved. Restore chance4 bait versus Japanese guaranteed2, success-only
bait consumption versus guaranteed fish, two-day trap versus Japanese daily collection,
current-harvest fertilizer scope versus growing-only placement, instant maturity,
primary giant yield change, and specific surface teleport placement restriction.
Literal +125%/+200% source values retained, not inferred total multipliers from titles.
Align tamed creature names with reviewed monster registry; preserve friendly relational
warmth versus physical-proximity heat and weapons-as-toys play. All shared regular/giant
crop descriptions read, not silently skipped or counted again as new coverage.
Source-language conflicts and runtime follow-up boundaries are in SOURCE_DATA_ISSUES.md;
this textual review does NOT measure actual catch/collection/fertilizer/teleport behavior.

Batch190:127 new equipment/device/furniture name-description occurrences, revised66/keep61.
Restore original flower return, special-barrel user immunity, mushroom storage cap and
three-total daily output, animal-treat collection, and actual keyboard timbre filters
instead of pitch-range change. Remove unsupported hellfire knockback, camera drop-proof
guarantee and bundled vanity tools. Keep rock-collapse combat distinct from mining.
Nine color-specific armor descriptions retain separate identities; commercial-secret
materials are not mystical ingredients. Restore silhouette furnishing, not a stage play.
Item narration is polite; quoted/player-clue voices elsewhere remain distinct.
Source-language disagreements do not prove runtime effects; see SOURCE_DATA_ISSUES.md.

Batch191:145 remaining item occurrences, revised86/keep59, all new coverage.
Item names883/883 and descriptions875/875 are now fully first-pass classified.
Match Karakasa Kozo item1216 to actual dialogue17995/17996 and daily2639/2652;
remove Nioh transliteration residue in material1468 in favor of registry 인왕.
Keep personal photo/memoir voices distinct from polite equipment descriptions.
Restore new-life arrival versus ancestral-home search, deserved human form versus
unsupported completed restoration, and tentative feelings versus a confirmed date.
Improve furniture/material/type labels, original head-canopy versus small-bed claim,
and source primary carpet heron/cloud scene versus auxiliary crane/water wording.
Original generic talisman1293 also links to blade1449/1452: logged as source wiring,
not guessed replacement prose. No object visual verification or live installation.

Batch192:100 custom UI occurrences0/1000..1098, revised8/keep92.
Restore HP recovery versus an increase, cannot-sow versus attempted failure,
next-week fan-mail wait condition, and primary unfinished-copy placeholder.
Core map/cooking/title/shop/quest controls reviewed as related flows; social
greetings retain voice. Custom-keyed exact selection now supported with rejection
tests. Three source-only labels1000OK/1034FOV/1078OK have individually pinned
six-locale/key/schema/fingerprint contracts; no generic ASCII or missing-text bypass.

Batch193:151 custom storage/husbandry/shrine/mail/save occurrences, revised15/keep136.
Align feeder material to actual item112짚, not a separate hay item; clarify no
depositable thatch in backpack versus nothing to put into backpack. Variable
key/name particles attach to stable button labels or separated recipients.
Clarify returned furniture mail attachments, not external computer files; remove
unsupported increased-room count and generic upgrade cost's house-only framing.
Four more individually pinned originals preserve HP/OK and original shrine-name
placeholders1134/1135. All seven custom contracts reject changed identity/schema/
any locale. Placeholder reachability remains a source follow-up, not invented lore.

Batch194:200 custom settings/relations/opening/casino/repair occurrences, revised27/keep173.
Read the complete thirteen-line opening as a coherent authoritative affectionate
clan address: restore unsettled life, actual survivors, transformation-specific
comparison, many strong forms not unlimited forms, and settled-in prerequisite.
Restore stranger rank, master/button volume, forging, farmhouse and countdown labels.
Preserve previous progress by entering existing game/manual-save BEFORE overwriting
autosave. Original alpha-test terms remain source content, not current policy advice.
Book-collection1451 gets one exact source-token repair for EN-derived italics absent
in JA. Current36 repairs remain individually keyed; fingerprints/token checks still
apply. Nine custom literal contracts now include original HP and NEW labels.

Batch195:200 custom slot/farm/input/demo/save notices, revised35/keep165.
Restore cannot-move-furniture-with-animals1545 versus copied positive home-fit JA/EN.
Restore primary slot attempts/current-score/effect-card reset scope, daily logs
versus future schedules, and farmhouse/book-page labels. Variable key particles
attach to stable button wording; charge attack, combat technique and affinity
labels align with actual source function and reviewed tabs.
Remove EN-only stale appended wishlist/survey/unreleased-spring text in demo1454,
preserving historical2025 and JA/global Discord reference. Migration notice1579
states game-side deletion, not a user file-deletion instruction. No files deleted.
SlimeSink/Float1632/1633 retain aligned exact key semantics and JA/EN against swapped
primary labels; runtime bindings untested. Eleven custom literal contracts now
include exact Lv prefix and confirmation, with no broad missing-text exemption.

Batch196:200 custom report/husbandry/appearance/object/social rows, revised26/keep174.
Nineteen existing corrections and seven explicitly registered missing mini-game
ready/go/game-over/result entries. Registry21 now seeds only verified original rows;
Korean authority remains TSV, never registry duplication. Payload total22,552.
Preserve daily TREAT scope, actual thatch/affinity/farmhouse labels, dynamic-action
particles, report-description field and optional screenshot checkbox. No report,
screenshot or upload performed. Valid 월하미인 stays aligned to reviewed room23144.
Flag1801 uses 폭풍파도단 from invitation2035/2057 and dialogue25387/25389; full-flow
callback16549/19607 for remaining Stormwave transliteration stays open.
Custom literal contracts13 now include exact UI/EXP, not untranslated mini-game prose.

Batch197:254 final custom occurrences, revised36/keep218; full custom1,105 now read.
Thirty-three existing revisions and three exact missing blackjack win/push/loss
entries. Registry24 and payload22,555 preserve source/fingerprint and frozen baseline.
Restore farmhouse-interior restriction, name-safe home joiner/wedding/hug messages,
overnight home invitation, favorite gift rank, crop giantification and filter names.
Explain pre1.0 Legacy Saves in ordinary Korean without removing continued-play
choice, bug/story/quest risks or new-game recommendation; no saved files touched.
Candy Disaster proper title stays, one exact37th source-token repair removes
EN-only italics. Custom literal contracts15 preserve NEW and ACE signature.
Seven interest_info references and named full-flow continuity callbacks remain;
full first-pass row coverage is not yet full objective completion.

Batch198:seven structural interest_info records, keep7, no text/payload mutation.
Original table7 u32-ID/seven-string records consumes1,824/1,824 bytes; apparent
locale fields are asset and localization references. All21 referenced strings are
already Korean with exact source fingerprints. Seven exact identity/schema/all-field
hash contracts preserve them; no generic identifier bypass. Fixed scope23,500 remains.

Batch199:six full scenes193 rows reread, revised21/keep172;18 new approvals,3 refinements.
Resolve five Nyotengu name residues, two Stormwave clan names and Mayor Yui31136.
Restore lighthouse REPAIR experience, learning new tales, non-compulsory enmity,
Shuten's own drinking boast, Kon health priority and Ama glamour/acting-skill tone.
Two names19055/19060 return exactly to pre-polish Korean: preserve approval history
but count them as unchanged versus baseline. Verifier now requires both exact keys,
fingerprints, before/after/old_target text and rejects unreviewed no-op approvals
or outside changes; five dedicated positive/negative tests pass.
First-pass coverage is complete. The named Manticore3451, loading62 cauldron and
pirate clan30657 callbacks below close in200/201. No overall completion claim yet.

Batch200:Leon108 plus Tor two-line full flows, revised22/keep88;16 new approvals,
six refinements. Restore romantic pursuit rather than exploration, actual alcohol,
unwanted-gift offering self-reproach, prayer/protection/rest/help meanings and
remove unsourced corrective instruction. Keep polite Leon, informal Kon, silent
birthday branches and separate relationship stages. Resolve Manticore3451 and
last Stormwave30657 naming residues. No new scope coverage or token exceptions.

Batch201:all31 loading hints reread, revised4/keep27;three new approvals,one refinement.
Restore explicit half-heart unit and crafting-tab cue; align Yokai Cauldron and
Smelting Furnace to original item names260/262/266. Align festival challenge label
and restore the oni camp warning, not invented doorkeeper role. Preserve earlier
source-conflict resolutions65/70. Cross-context final QA remains distinct from
first-pass classification and source/runtime follow-ups; no goal-complete claim.

Batch202:whole six-row UI tutorial reread, revised1/keep5. Five exact original
item links establish Universal Dye25125 versus fruit/flower extraction bath3444.
Fix free-color tutorial12 under exact source/key/token contract with three new
idempotence/source/token/identity regression tests; no generic token-rule change.

Batch203:35 complete repeated item-key occurrences, revised17/keep18. All17 groups
have identical six-locale source and same surface; preserve every identity, not
destructive deduplication. Align Nioh to actual monster8 인왕, L-shaped screen and
paper numbering, plus resource descriptions and shared generic shelter body.

Batch204:nine linked book/title/three-volume occurrences, revised3/keep6. Propagate
accepted later107/108 to identical-source47/49. Restore rockfall sealing sole exit
and sacred-water accusation in48. Keep historic Kuzunoha distinct from Kuzuha,
weekly two-year covenant then lifelong voluntary friendship. No lore invented.

Batch205:93 Torleone daily plus24 friendship-tutorial and Anna intro1, revised8/keep110.
Original94 name-key references establish actual NPC IDs, not translated row numbers:
4206 Torleone,4207 Seabert,4218 Anna. Fix name particles/copula, unknown-player-name
topic construction, core-crew esteem, healthy-growth wish, first-morning beloved
face, farmhouse decoration versus creating fish smell, and restful sleep.

Batch206:whole Kinntarou_02 quest title/body, revised1/keep1; fixed Torleone subject
particle without touching two-carp/three-potato quantities or Shuten chef role.
202-206:170 reread occurrences,30 revisions;22 new approvals,eight refinements.
No new coverage or outside-batch changes. Whole-payload repeated-key Korean
conflicts now zero. Source-backed particle callbacks23911/24305/24307/24309 close
in207/208 below. No whole-goal completion claim.

Batch207:whole272 Sasaki heart rows reread, revised6/keep266. Fix Seabert particle,
respectful Maya references without premature species assertion, daily singing
request, nonmanual order-completion question and canonical Mountain Tree label.
Keep deliberate Kon teasing and kiss response, plus Alin's conditional theory.

Batch208:whole356 Shuten heart rows, revised11/keep345. Fix last three particle
callbacks, entrusting group planning rather than handling it herself, lack of
previous heist experience, fizzy drink, clan/place names and actual treehouse.
Retain deliberate earlier cover story versus later Red Oni confession and distinct
forest/casino memory variants; do not flatten them into a single runtime sequence.

Batch209:whole initial55 Kincho date rows reread, revised4/keep51. Restore primary
personal familiarity boundary instead of Japanese-only blanket bathing taboo,
Seikyu settlement, cozy winter response and endless-war cost. Frozen legacy55
remains untouched. New packet explicitly records ellipsis22819 as original text,
not null; all latest records now carry exact source triples and wording.
207-209:683 reread rows,21 new approvals. Static base-NPC directly attached
particle scan now has zero mismatches. This is not alias/runtime name coverage.

Batch210:three full tree-rest/purification flows146 rows, revised7/keep139.
Use canonical Mountain Tree without inventing deity names; retain Maya's tree
where the source actually says it, resident offerings and builder-specific request.
Batch211:whole Leon heart134 rows, revised5/keep129. Align three Alin references
with actual NPC name82, canonical tree and distant ceremony observation; restore
the chili/stew affectionate callback while retaining uncertainty and choice branches.
Batch212:whole Tsukimi Festival268 rows, revised2/keep266. Restore the tree as
goddess symbol rather than invented planted memorial; align blessing UI term 은혜.
210-212:548 reread rows,14 revisions,11 new approvals/three refinements; no new scope.

Independent immutable-history audit passes through212:210 complete packets,
all input/output payload and TSV links, config/control hashes, exact selected
identities, decisions and row transitions. All23,500 latest decisions agree with
current canonical/frozen source; no unexplained partial, hold or outside mutation.
Six auditor transition tests reject missing changes, extra/deleted rows, source
metadata mutations and disguised overwrites. See polish_history_audit.json.
This evidence proves records/merge coverage, not semantic reading by itself.

Closed semantic callback queue:Mountain Tree references15689/19456/19457/19876/
19904/19906/19912/20564/23037 across five full flows:Dialog_116005463442194432,
CH2B_Q2.8,CH3_Q3.10,CH3_TsukimiFestival,Leon_heart_4_2_20.20564 actually names
Yamabiko in primary and19904 says Maya's tree; do not globally erase deity names.
All nine references resolved in210-212; no open editorial callbacks. Current
editorial_scope_complete is true only while exact completion/history hashes,
all six requirement reviews, full coverage and no-hold checks agree. Seven
completion-gate tests reject stale, partial or unsupported completion claims.

Validation:65 focused generator/review-contract tests plus5 baseline-restoration,
6 immutable-history transition and7 completion-gate tests pass (83 total);
4,957 serialized Korean strings read
back exactly; unapproved text changes 0; existing identities/fingerprints unchanged.
Twenty-four exact approved original-row additions are independently validated against source.
No invisible Unicode format characters in cumulative approved targets; Ruff passes.
No cumulative approved hits for locked forbidden terms 청궁/청람/칭란/흑호/영화물어
or residual Japanese first-person 와타시.
An initial test invocation hit sandbox temporary-directory write restrictions;
the same unmodified suite passed with normal temporary-directory permission.
Temporary clean export/installation, font inspection and exact restore passed
at the4,957-approval milestone, alongside serialized text verification.
Restored excel/bag hashes match both clean originals exactly. The prior1,138/
1,384/1,583/1,824/1,960/2,094/2,222/2,306/2,501/2,596 milestones are historical.
Latest full temporary installation milestone4,957 passed serialization/readback and installation/
restore; see temp_integration_after212.json for current hashes and exact byte
restoration. Reusable audit/run_clean_temp_check.py pins clean originals and
verifies BOTH live excel/bag files unchanged, plus exact restored temporary hashes.
Earlier checkpoints remain historical.
The current4,957 approvals passed serialization/readback and temporary install/restore
after212, including exact baseline-restoration checks. Closed naming residues
아린/뇨텐구/폭풍파단/스톰웨이브단/맨티코어 are absent from the entire current payload.
No actual live-game visual claim.
Current37 exact source-token repairs are separate
from three exact original-Japanese markup repairs, two exact original-Japanese
token repairs (one player-vocative, one dye item reference), twenty-four registered missing rows, and eight source-verified
literal-identifier passthroughs plus six exact table-literal passthroughs
(not new payload translations).
Forge schema/gate was unavailable in configured roots; scoped implementation contract
is `.forge/polish_addition/spec.json`. No Forge gate PASS is claimed.
At the editorial-only checkpoint, font inspection checked structure/references,
not rendered gameplay; no EXE rebuild, version bump or publication was performed.
Subsequent v0.1.18 packaging/live-install checks are recorded at the top of this
document and in release-v0.1.18.md. Actual visual gameplay verification remains open.
