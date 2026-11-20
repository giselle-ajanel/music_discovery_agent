# Music Discovery Agent: Test Results

Agent: Music Discovery Assistant (Neo4j Aura Agent, Internal access)
Graph: 1,028 artists, 210 bands, 1,142 MEMBER_OF relationships (Wikidata, CC0)
Test date: 2026-11-18

## How to score

Ask each question in a New chat. Compare the answer with the expected result below, which was checked against the CSV.

- Correct: gives the graph's answer and nothing contradicts the graph. Extra outside facts are allowed but noted.
- Partial: gives the graph's answer but also states something that contradicts the graph, or misses part of it.
- Wrong: wrong facts, invented names, or an error.

Final score = Correct / 20. Partial does not count toward the score but is noted.

Also note in Notes if the agent needed more than one try (errors or retries before answering).

## Version 1 results (broken tools)

Questions 1 to 4 were scored on the first agent, which was created with Aura's "Create with AI" option. Expanding the agent's reasoning showed that all three Cypher template tools failed inside the chat with "parameter(s) is missing", even though each tool passed when tested by hand. Because its tools failed, the agent answered from the model's general knowledge instead of the graph. That explains the outside facts and the contradictions in questions 1, 2, and 4.

Version 1 score: 1 Correct, 1 Partial, 2 Wrong (4 questions asked).

| # | Version 1 result | Version 1 notes |
|---|------------------|-----------------|
| 1 | Partial | Correct connection; added facts not in the graph (bass, albums, songs, 1971) |
| 2 | Wrong | Took 3 tries. Answered from outside knowledge (duet, friendship) and said Stevie Nicks never joined the band, which contradicts the graph |
| 3 | Correct | Connection, roster, roles, and 2009 match the graph. Added outside facts (Kyuss, album, Grammy, touring) |
| 4 | Wrong | Called the link "cultural influence" rather than shared members, which contradicts the graph. Missed the 4-hop path |

## Version 2 results (working tools)

Test date: 2026-11-19. Same agent with the corrected tools and the grounding prompt (answer only from tool results, no added albums, years, or history). Rebuilding from scratch turned out not to be needed: on retry the tools ran in chat and returned graph results. The Results table below holds the Version 2 scores; Version 1 scores are kept in the table above.

## Results

| # | Question | Tool expected | Expected result (from the data) | Result | Notes / fix |
|---|----------|---------------|----------------------------------|--------|-------------|
| 1 | How is David Bowie connected to Trevor Bolder? | Connection path | Both in The Spiders from Mars (2 hops) | Correct | Correct connection, short answer, no albums or years. One outside phrase: called the band Bowie's "backing band", which is not in the graph |
| 2 | How is Stevie Nicks connected to Tom Petty? | Connection path | Both in Tom Petty and the Heartbreakers (Nicks as Guest Vocals, ConnectionType Collaborator) | Correct | Matches the graph exactly: Nicks Guest Vocals, Petty Guitar / Voice. "Performed as a guest" is drawn from her Collaborator row, not outside knowledge. Answered on the first try. Version 1 said she never joined, from memory |
| 3 | How is Josh Homme connected to John Paul Jones? | Connection path | Both in Them Crooked Vultures | Correct | Matches the graph exactly: Homme Guitar / Vocals, Jones Bass. No outside facts (Version 1 added Kyuss, album, Grammy, touring) |
| 4 | How is Nirvana connected to Paramore? | Connection path | Nirvana > Dave Grohl > Foo Fighters > Josh Freese > Paramore (4 hops) | Correct | Full 4-hop path with roles exactly as the graph lists them (Drums; Lead Vocals / Guitar; Drum Kit). No outside facts. Was Wrong in Version 1 |
| 5 | How are Deep Purple and Kansas connected? | Connection path | Steve Morse played in both | Correct | Steve Morse, Voice / Guitar in both, exactly as the graph lists. No outside facts |
| 6 | How are The Clash and Gorillaz connected? | Connection path | Mick Jones played in both | Correct | Mick Jones: member of The Clash (Guitar / Vocals), collaborated with Gorillaz (Guitar). Roles and Member vs Collaborator distinction match the graph. No outside facts |
| 7 | Who was in King Crimson, and what did they play? | Band roster | 14 members, incl. Bill Bruford, Greg Lake, Ian McDonald | Correct | All 14 members, every role exactly as the graph lists. Kept Greg Lake as Acoustic Guitar / Harmonica (a Wikidata quirk) instead of "correcting" it from memory, which shows it stays grounded |
| 8 | Who are the members of Foo Fighters? | Band roster | 7: Chris Shiflett, Dave Grohl, Ilan Rubin, Josh Freese, Nate Mendel, Pat Smear, Taylor Hawkins | Correct | All 7 members, every role exactly as the graph lists. Kept Taylor Hawkins as Piano / Guitar (Wikidata quirk; he was the drummer) |
| 9 | Who was in Led Zeppelin? | Band roster | Jimmy Page, Robert Plant, John Paul Jones, John Bonham (plus Jason Bonham) | Correct | All 5 members including Jason Bonham (reunion data), every role exactly as the graph lists. Did not trim to the well-known 4 from memory |
| 10 | What instruments did the members of Deep Purple play? | Band roster | 12 members with roles | Correct | All 12 members, every role exactly as the graph lists. Did not add Voice for Ian Gillan or David Coverdale from memory |
| 11 | Which bands share members with Jethro Tull? | Other projects | Uriah Heep, via John Glascock | Correct | Only Uriah Heep via John Glascock (Acoustic Guitar / Keyboard Instrument), matching the graph. No extra bands added from memory |
| 12 | What other bands did Foo Fighters members play in? | Other projects | Nirvana, Paramore, Queens of the Stone Age, Them Crooked Vultures, Weezer | Correct | All 5 bands with the right member and role (Grohl: Drums; Freese: Drum Kit). No bands outside the graph (e.g. Germs, Nine Inch Nails) |
| 13 | What other projects are Soundgarden members part of? | Other projects | Audioslave, Bam Bam, Pearl Jam | Correct | All 3 bands with the right member and role (Cameron: Drum Kit; Cornell: Guitar / Voice). Did not add Temple of the Dog, which is not in the graph |
| 14 | What other bands did Deep Purple members join? | Other projects | Flying Colors, Kansas (via Steve Morse) | Correct | Both bands via Steve Morse (Voice / Guitar), matching the graph. Did not add Rainbow, Whitesnake, or Black Sabbath, which are not in the graph |
| 15 | Which musicians have played in the most bands? | Text2Cypher | Dave Grohl and Mick Jones (4 each) | Correct | Mick Jones and Dave Grohl at 4, then three artists at 3, all counts match the graph. Showed 3 of the 8 artists tied at 3 (likely a LIMIT in the generated query) without saying the list was cut off. Mick Jones's 4 merges two different musicians with the same name (see Known data limits) |
| 16 | Which bands have the most members in the graph? | Text2Cypher | A.R. & Machines (27), Santana (26), Jethro Tull (20) | Correct | Top 5 counts all match the graph. Fifth place is a tie (Toto and King Crimson at 14); showed only King Crimson without noting the tie (same LIMIT 5 pattern as Q15) |
| 17 | How many progressive rock bands are in the graph? | Text2Cypher | 21 | Wrong | Said no bands have the genre "progressive rock". The graph stores it as b.genre = 'Progressive Rock' (Title Case), and the generated query (confirmed in the tool's Test tab) was MATCH (b:Band {genre: 'progressive rock'}), an exact lowercase match that returns 0. It did not invent a number, but the answer is wrong. Fixed after scoring (see Fixes); retest returned 21. Score kept as Wrong |
| 18 | What genre is Deep Purple, and when were they formed? | Text2Cypher | Hard Rock, 1968 | Correct | Hard Rock, formed 1968, matching the graph. No outside facts |
| 19 | How is Taylor Swift connected to The Beatles? | Any (should refuse) | Neither is in the graph; agent should say it can't find them | Correct | Said no connection was found in the graph and did not invent one. Small gap: it did not say that neither name exists in the graph, which is the more precise answer |
| 20 | Who was the drummer for Nirvana? | Band roster or Text2Cypher | Graph lists 6 drummers: Dave Grohl (Drums), Aaron Burckhard, Dale Crover, Dave Foster, Dan Peters (Drum Kit), Chad Channing (Bass Guitar / Drum Kit) | Correct | Listed all 6 drummers with roles exactly as the graph lists, instead of answering "Dave Grohl" from memory |

Final score (Version 2): 19 / 20 correct (0 partial, 1 wrong)

Version 1 for comparison: 1 / 4 correct (1 partial, 2 wrong), with all three Cypher tools failing in chat.

Pattern notes:
- All 14 template-tool questions (connection path, roster, other projects) were Correct. The agent repeated graph roles even when they differ from well-known facts (Greg Lake, Taylor Hawkins, Ian Gillan), which shows it answers from the graph rather than memory.
- The one miss (Q17) came from Text2Cypher, where the model writes its own query: a case-sensitive genre match returned 0.
- Text2Cypher top-N answers (Q15, Q16) cut off ties at the limit without saying so.
- After fixing the genre match, Q17 returns the correct count (21), so the post-fix result is 20 / 20 on retest of the one failure.

## Fixes made during testing

| Issue | Cause | Fix | Result |
|-------|-------|-----|--------|
| Agent errored on connection questions | AI-generated tool used parameter names (entityName1) that did not match the query ($entity1_name) | Renamed parameters to match; changed query to return plain names, roles, and hop count instead of raw path objects | Bowie to Bolder now returns the path through The Spiders from Mars |
| Other-projects tool could repeat one band many times | One row per member and band, then LIMIT 10 | Grouped results by band and sorted by shared members | Up to 10 distinct bands per answer |
| Relationships did not load on first import | Importer mapped the Band end of MEMBER_OF to the ConnectionType column | Loaded relationships with LOAD CSV in Query, matching on BandName | 1,142 relationships |
| Agent ignored the graph and gave outside facts or wrong answers | All three Cypher tools failed in chat with "parameter(s) is missing"; the agent fell back on general knowledge | Corrected tool parameters and query outputs, tightened the prompt to answer only from tool results | Version 2: tools run in chat; Nirvana to Paramore went from Wrong to Correct |
| Q17: "How many progressive rock bands" returned 0 | Text2Cypher generated MATCH (b:Band {genre: 'progressive rock'}), an exact lowercase match; genres are stored in Title Case ('Progressive Rock') | Added the Band schema and a rule to match genre case-insensitively (toLower) to the Text2Cypher tool's configuration | Retest in a new chat: "There are 21 bands in the graph that are classified as Progressive Rock." Correct |

## Known data limits


- Roles come from each artist's instruments on Wikidata, not their role in a specific band (for example, Greg Lake shows "Acoustic Guitar / Harmonica" for King Crimson).
- Some band rosters include later or reunion members.
- 53 bands have genre "Unknown" and 75 have no formed year.
- The graph covers 1,028 artists, so many real connections between bands are not included.
- Artists are matched by name only, so different people with the same name share one node. Mick Jones of The Clash (The Clash, Gorillaz) and Mick Jones of Foreigner (Spooky Tooth, Nero and the Gladiators) are merged, which makes "Mick Jones" look like he played in 4 bands. A fix is to key artists on their Wikidata ID instead of their name.
- In Version 1 the agent added background knowledge not in the graph, mostly because its tools were failing (see Fixes). In Version 2, with working tools, outside facts dropped to one phrase across 20 answers ("backing band" in Q1).
- Bands are also matched by name only. The Nirvana node merges Kurt Cobain's Nirvana with an unrelated 1960s British band named Nirvana (Patrick Campbell-Lyons, Ray Singer).
