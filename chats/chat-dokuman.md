Set up, I wanna make a tool. I wanna make a documentation tool. You point it at any repository, or you point it at any folder, or you point it at any set of files, you point it at anything that gives the user a capability that they interact with, anything, and it analyzes it, it inspects it. And so, there's strict subagent discipline. We spawn a sub we spawn one or more subagents to inspect the artifacts, and the model should use its best judgment on how many subagents it's gonna need based on the amount of material. So the first thing that it does is it does reconnaissance, right? Like it, it spawns one subagent to scan. The directory, or to look at the inputs, or to check the web, or whatever it is, but it, you get one subagent and it assesses and it puts together a little report for the main context, just to lay the lands, you know, just a light report, but it has enough information so that the main context can have an idea of how it needs to orchestrate. Okay, now next stage. Now, we do, the main context will spawn one or more subagents and it will inspect the material. And what it's doing, it's, it's going through everything. If it's source code, it's looking at features. If it's an instruction manual, it's looking at, you know, what the thing does. If it's a design document, then it's inferring what the features are. But whatever it is, it goes through and the, the prompt itself is gonna be very light. We're gonna delegate to the frontier model, we're gonna give it the responsibility of figuring this out. The frontier model's smart, we don't have to overspecify. But what we're doing is, is we wanna extract The features. And a feature is one sentence that explains a capability that the thing does. And Something that Is adjacent to the user, right? And but it's not something that's like stupid, right? Like for example, like a text editor, we know that text editors save files. You don't have to, that's not a, we don't have to tell the user about that feature, it's just assumed. It's like, what does, what does this thing do that distinguishes it from the other things in its genre, right? Or In other words, we scan it, we scan it, and we extract the features. And we do it in the form of sentences, and. It's just like, okay, here's a feature that allows you to control the size of the chunks. That's like, that's a feature, right? Or another one might be, this one lets you choose the language of the translation. That's a feature. Now, if we're looking at code, we can infer the features. We can look at, we can see if there's a public function, we can see if there's a command line switches, you know, we can extract those. And the frontier model, like I said, is not stupid. And, and it should on the side of extracting two more features rather than Than less, 'cause we don't wanna miss anything. But if we get too much, we can cut some out. Okay, so now the sub-agents, we combine that list, so now we have the master list. And that goes in a scratch file. Then we spawn another sub-agent, and now we go through that list, and we need to We need to order it and sort it. So the goal now is, we have this big list of sentences, maybe there's a hundred, two hundred items, and the goal is we wanna group it. What is the top level feature? What is and how do we find out the top level feature? That is the feature above which there's no other feature that controls it. It's like a root feature, right? It's like there's no other feature that can configure that, that can cause its behavior to change, right? It's like a fundamental thing. So that's tier one. And the tier two features are the ones that are the direct consequence of the tier one, right? Like they have one Predecessor that can control them. And then the tier three is like one below that, so it's a hierarchical set of features. Now, if we were gonna explain the product in a thirty-second elevator pitch, we would tell it the tier one. If we were gonna explain the product in a five-minute talk, lightning talk, we would give them tier one and tier two. If we were gonna give a one-hour talk, we would give tier one, tier two, and tier three. So we have that each sentence has the tier, and then we need to order the dependencies. In other words, what order do we, do we wanna explain? So if feature A Has to, is required to understand before feature B, then we set it ordering. So now the goal is to output a new scratch file that has all the sentences numbered, and they start from one, and it's dependency ordered, and it's also sectioned. So we have section one, tier one, is the first section, and then we have all the numbers, and then tier two is the next section, and it continues the numbering. So if we stopped at twenty in tier one, now we start at twenty-one in tier two. Okay, now we keep numbering, now we keep going. So now we have it all All numbered. Okay, great. So now we have that scratch file, and now that becomes the template, and we did that in the subagent. Now that becomes a template for actually writing the documentation. So now we're gonna take the report approach, we're gonna say, okay, we're gonna do the executive summary, we're gonna basically compress everything into one brutal paragraph, and that's gonna explain what the thing does. Then what we wanna do is we wanna have major sections. We have a, we have a subsection that explains the tier one Features at a high level. We just have like a couple of sentences for each one. We explain it at the, at the tier one level. Then we go, now the rest of it is gonna be an explanation of the thing. And that's what we're gonna use the frontier model is just gonna start writing. It's gonna explain each feature and it's gonna use its best judgment on how it wants to explain it. But the approach is gonna be a progressive level, a progressive revelation, where we talk about the tier one and tier two, but the explanation is in terms of the actual nuts and bolts of it, the mechanics, the tier three. Do you understand what I'm talking about? Analyze my idea, think about what I just told you, spawn multiple sub-agents, and search the web for established practice on automated generation of documentation of artifacts. And see if my ideas hold up, and see how it can be tweaked and tuned.

---

Okay, so now what I'm talking about is I want to Let me take a look at this here. Right, okay, so for the writing instructions, the I wanted to ground itself in a statement. I wanted to say, "You are. . . " A technical writer. Task producing documentation, you write in a way that is understandable and legible for beginners and experts alike. You adapt your Complexity to the material: simple material is written for simple readers, complex material is written for complex readers. To measure the level of complexity, you answer the question: How much knowledge would someone need to know to understand the domain that this tool operates in? That doesn't have to do with that's not specific to the tool. Do you understand? Read back to me the writing instruction and tell me what you think.

---

I think, I think that's very good. And also, I wanna make sure that I want the frontier model to naturally build examples one at a time, where each example is a single teachable principle, and the examples throughout are ordered in such a way that they start from the most basic thing, like a hello world, and then they progress until the very end you see the maximum complexity. But I want the frontier model has to use its own judgment, because we don't want like a million examples. Like if there's too many features, it has to be selective, like it needs to group them. If there's not enough features, it has to be smart about how I gotta present that. Let me show you an example of a really great user guide.

---

the name of the tool is dokuman.md

Dokuman

The first 2 paragraphs should be this really ornate stylish prose that is 85% english and the other 15% is a mixture of actual and made up words and phrases of romance languages freely mixed with emphasis. do you understand? Show me a few different sentences and I will choose to lock the style, then you will propose the both paragraphs. the first paragraph describes the second one explains.

---

I love B and D. Let's do D for paragraph 1, B for paragraph 2

---

do not use any dashes

---

perfect

---

Okay, so now what I'm talking about is I want to give the writing discipline. So the writer, in all cases, I mean, this is just a general rule, when we write, we want the writing agent to have the least amount of terms of analysis. first of all, diachesis is garbage. That's, that's a fucking garbage. It's unfalsifiable bullshit. Okay, now back to the thing. So what so the goal, and this is a general rule, the goal is we wanna create a evidence packet, right? We wanna create a writing packet of information that's stated in flat sentences, like declarative and descriptive sentences. They don't tell they don't, they're not speaking to the user, they're just statements of fact. And there's a, there's a little bit of structure there. And then we put that in a subagent, a fresh subagent, one subagent, just one, and we give it writing instructions via XML-tagged external reference. We give it the evidence file, which is a scratch file that has like the packet, and then we give it the template, we give it a reporting template. And I think, I think the main context should orchestrate the reporting template. It should write the reporting template into a file, and then it should give the subagent, the reporting agent, a pointer to that file. And here's why, because one report template isn't gonna be ideal for all content. We should just let the main context spend some tokens and figuring out the shape. But there's gonna be some things that should always be there. So figuring out, figuring out what every report should have in common, like we, we, we need a, the first paragraph has to grab the user and sell them on the product. Of course, obviously. We gotta get them excited. They have to understand what it is, why it's great for them, and what they're gonna be able to accomplish if they read. That goes without saying. Then, you know, whatever's the best established practice, we give a few different shapes that, that, this is kinda generally works for everything, and then This main context will choose a report template, it'll write it out, you know, it'll have the headings already there, and it'll just have instructions that'll say, "Hey, fill this in." Then we pass that to the sub-agent.

---

I think, I think that would help? Like. If I told you that you're a teacher who operates in the technical writing register, would that land differently for you? How would that land?

---

Okay, so now I wanna give the writing discipline. So one failure mode is being like just telling the AI, "Okay, document this." Obviously, that's foolish because it's so open-ended and vague. So Another failure mode is someone does a really rigid architecture, like, "Oh, I'm gonna do it. I'm gonna specify everything, and we're gonna get everything." And they aim to be overly complete, and models have a problem when you try to make them complete. Then they get hung up. They think too much. They produce too much. The con the hunt for completeness consumes the thinking budget. I wanna avoid those failure modes. I wanna give the model, I wanna give the doc Documentation model room to breathe. I want it to somehow be okay with incompleteness when the incompleteness is in the service of providing documentation that's good enough and doesn't have to be perfect. But I don't We need to be careful that we don't give an instruction that's so loose that it just starts leaving shit out. So give me five options on how to achieve this. Give me five heuristics that are unambiguous that will make this thing produce documentation that's good enough. And the understanding is this, no The dream, the dream is to be able to point it at a repo and get documentation and be done and be perfect. That's never gonna fucking happen. There is no way that a large language model will ever consistently produce perfect documentation that doesn't need editing by a human later. So the target, I wanna target something that's good enough for someone to read and get an understanding and a great starting point for a human. I call that the eighty percent solution. In other words, a starting point for a human editor to take the, to get the last twenty percent. It just has to be good enough to get to the eighty percent solution. Do you understand? Think about that deeply. Give me the options.

---

A, B, C, and E land for me. The what would you google is not really landing.

---

Okay, here's what I want you to do. I want you to take Everything that I said in this chat, every one of my, every one of the turns, I want you to take what I said and I want you to lay it out sequentially in one. Blob. And then what I want you to do is for each For each element of chat, I want you to extract the rationale or the implied rationale from it. In other words, I want you to form a series of sentences that explain the behavior of the tool and why it's that way. Do you understand? And I want you to give me a numbered list. You're gonna give me a numbered list of sentences that are facts about this entire conversation. You're gonna go through this whole conversation, but only the things that I said. I don't care what you said, I only care about what I said. So for each chat, you look at all the text in that one, my one prompt, and you form all the questions from it. You say the qu you, sorry, you form all the sentences from it. Each sentence says a fact about the design and the, the, and the why, the implication, and it can be two sentences if you necessary, fe or try to make it one though. And I want those to be numbered bullets. Do that now.

---

Here's what I want you to do: I want you to take this list of fifty two. designs, and I want you to compress it down into Three groups with two paragraphs per group, and sort them so that they're thematically grouped. And, and, and in other words, come up with three groupings, assign them into the each group, and then write the two paragraphs for that group that's formed by compressing all the sentences together and describing the tool and its behavior in terms of how it supports, the reason that it supports the sentences that were compressed. each paragraph should have short declarative sentences with at most one connecting phrase. One sentence can have two connectors. Give each group a subhead but do not mention the group number. do it now.

---

the very bottom of the tool will have a separate followed by those three subsections above

---

## Tool Design

This explains the choices used to write the tool.

### Extraction and Organization

...

(generation date and model slug, in italics)

---

now make the plan self contained by pulling everything you need from this chat into the plan file

---

how much reasonining should we execute with? I'm thinking Opus 4.6 Medium with 1M context

---

higher thinking makes the writing worse not better

---

review the plan. spawn multiple subagents and search the web for best practices. I want this prompt to be short and sweet. nothing unnecessary. prefer to cut rather than add. A light touch. After the subagent plan enrichment, run the prompts-rulebook and compress.

---

Okay, here's what I want you to do: I want you to go through The whole, I-my ideas versus established practice, and I want you to correct each of my ideas and use the established practice. So I want you to basically rewrite, rewrite the entire plan, and I want you to bake in all of the, all that research that you found and use it to fix everything. I wanna trust you completely. Any trace of my old stuff, I just want the plan to just be clean and just explain exactly how it should work. None of the old stuff, no explanations. I mean, there could be a couple, there could be a few sentences here and there explaining the why, 'cause that'll ground the model, right? In other words, when you, when the, when the plan has an instruction, you explain the reason so then if, when the model goes to execute, and if it gets confused, it can look at the reason to ground it. Do you understand?

---

create a large portrait image with three sections. a top half, and the bottom half divided into two horizontal slices. so by height: 50%, then 25%, then 25%. the image represents the tool. the top panel is a classroom with empty seats and a humanoid robot teacher with two articles of cyberpunk teacher's clothing for style, no humans in the scene. the middle panel is a data tablet zoomed in to show a teaching user interface with terminology from the plan. a cool futuristic user interface. the bottom panel is a collection of architectural parts which represent building blocks for a bigger thing.

After creating the image, slice it horizontally into three pieces. at the seams. one cut at 50%, the other cut at 75%, give them names images/dokuman-1.png, dokuman-2.png, dokuman-3.png and insert markdown references to these images in the tool itself when generated. The first image goes after the 2 paragraphs. Put the second image around the middle of the file just before a section heading. Put the last image just before the Tool Design content
