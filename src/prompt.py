SYS="You are a helpful assistant."

ZS=(
    "[Instruction] Only print your answer directly without any explicit reasoning steps. You should provide your answer strictly after an [Answer] tag."
    "[Problem] {problem}\n\n"
)

ZS_CoT=(
    "[Instruction] Break down your reasoning process step by step, show your thought process explictly. You should provide your answer strictly after an [Answer] tag."
    "[Problem] {problem}\n\n"
)

# FS_CoT_GSM=(
#     "[Examples]\n"
#     "Example 1: \n[Problem] Nida has 50 chocolates in which some are in 3 filled boxes and 5 pieces are not in a box. Her friend brought 25 pieces of chocolates. If all chocolates must be placed in a box, how many more boxes do they need?\n"
#     "[Solution] \n1. There are 50 - 5 = 45 chocolates in three boxes.\n2. So, each box is filled with 45/3 = 15 chocolates.\n3. 5 + 25 = 30 chocolates are needed to be placed in boxes.\n4. Hence, they needed 30/15 = 2 boxes for the 30 chocolates.\n[Answer] 30.\n\n"
#     "Example 2: \n[Problem] Julia bought 3 packs of red balls, 10 packs of yellow balls, and 8 packs of green balls. There were 19 balls in each package. How many balls did Julie buy in all?\n"
#     "[Solution] \n1. The total number of packages is 3 + 10 + 8 = 21.\n2. Julia bought 21 * 19 = 399 balls.\n[Answer] 399.\n\n"
#     "Example 3: \n[Problem] Jo-Bob hopped into the hot air balloon, released the anchor rope, and pulled on the lift chain, which ignited the flame and provided the warm air that caused the balloon to rise.  When the lift chain was pulled, the balloon would rise at a rate of 50 feet per minute.  But when the chain was not being pulled, the balloon would slowly descend at a rate of 10 feet per minute.  During his balloon ride, he pulled the chain for 15 minutes, then released the rope for 10 minutes, then pulled the chain for another 15 minutes, and finally released the chain and allowed the balloon to slowly descend back to the earth.  During his balloon ride, what was the highest elevation reached by the balloon?\n"
#     "[Solution] \n1. The first 15-minute chain pull caused the balloon to rise 50*15=750 feet.\n2. Releasing the chain for 10 minutes caused the balloon to descend 10*10=100 feet.\n3. The second 15-minute chain pull caused the balloon to rise another 50*15=750 feet.\n4. Thus, at the end of the second chain pull, when the balloon was at its highest elevation, the balloon had risen to an elevation of 750-100+750=1400 feet above the earth's surface.\n[Answer] 1400.\n\n"
#     "[Answer] 1400\n\n"
#     "[Problem] {problem}\n\n"
#     "[Instruction] Break down your reasoning process step by step, show your thought process explictly. You should provide your answer strictly after an [Answer] tag."
# )


FS_CoT_GSM=(
    "[Examples]\n"
    "[Example Problem 1] Nida has 50 chocolates in which some are in 3 filled boxes and 5 pieces are not in a box. Her friend brought 25 pieces of chocolates. If all chocolates must be placed in a box, how many more boxes do they need?\n"
    "[Solution] \n1. There are 50 - 5 = 45 chocolates in three boxes.\n2. So, each box is filled with 45/3 = 15 chocolates.\n3. 5 + 25 = 30 chocolates are needed to be placed in boxes.\n4. Hence, they needed 30/15 = 2 boxes for the 30 chocolates.\n[Answer] 30.\n\n"
    "[Example Problem 2] Julia bought 3 packs of red balls, 10 packs of yellow balls, and 8 packs of green balls. There were 19 balls in each package. How many balls did Julie buy in all?\n"
    "[Solution] \n1. The total number of packages is 3 + 10 + 8 = 21.\n2. Julia bought 21 * 19 = 399 balls.\n[Answer] 399.\n\n"
    "[Example Problem 3] Jo-Bob hopped into the hot air balloon, released the anchor rope, and pulled on the lift chain, which ignited the flame and provided the warm air that caused the balloon to rise.  When the lift chain was pulled, the balloon would rise at a rate of 50 feet per minute.  But when the chain was not being pulled, the balloon would slowly descend at a rate of 10 feet per minute.  During his balloon ride, he pulled the chain for 15 minutes, then released the rope for 10 minutes, then pulled the chain for another 15 minutes, and finally released the chain and allowed the balloon to slowly descend back to the earth.  During his balloon ride, what was the highest elevation reached by the balloon?\n"
    "[Solution] \n1. The first 15-minute chain pull caused the balloon to rise 50*15=750 feet.\n2. Releasing the chain for 10 minutes caused the balloon to descend 10*10=100 feet.\n3. The second 15-minute chain pull caused the balloon to rise another 50*15=750 feet.\n4. Thus, at the end of the second chain pull, when the balloon was at its highest elevation, the balloon had risen to an elevation of 750-100+750=1400 feet above the earth's surface.\n[Answer] 1400.\n\n"
    "[Your Problem] {problem}\n\n"
    "[Instruction] Break down your reasoning process step by step, show your thought process explictly. You should provide your answer strictly after an [Answer] tag."
)


FS_CoT_HQA=(
    "[Instruction] Break down your reasoning process step by step, show your thought process explictly. You should provide your answer strictly after an [Answer] tag."
    "[Examples]\n"
    "[Example Problem 1] Did Ed Sullivan ever work anywhere other than the New York Daily News?\n"
    "[Solution] \n1. Ed Sullivan is widely recognized for hosting \"The Ed Sullivan Show.\"\n2. Before TV, he was a journalist, notably at the New York Daily News.\n3. Hosting a TV show indicates employment beyond newspaper journalism, confirming he worked outside the New York Daily News, specifically on \"The Ed Sullivan Show.\"\n[Answer] The Ed Sullivan Show.\n\n"
    "[Example Problem 2] Pravda and Stiffelio are both operas?\n"
    "[Solution] \n1. \"Pravda\" does not refer to a known opera. The term \"Pravda\" is most commonly associated with the Russian word for \"truth\" and is the name of a major newspaper in Russia.\n2. \"Stiffelio\" is indeed an opera, composed by Giuseppe Verdi, with its premiere in 1850. \n[Answer] no.\n\n"
    "[Example Problem 3] Who can play more instruments, Michael Monroe or Alison Goldfrapp?\n"
    "[Solution] \n1. Michael Monroe is primarily known as a Finnish musician, best recognized as the lead vocalist and saxophonist for the rock band Hanoi Rocks.\n2. He's instrument skill set is known for vocals, saxophone, harmonica, keyboards.\n3. Alison Goldfrapp is an English musician, singer, songwriter, and record producer, known as one-half of the electronic music duo Goldfrapp.\n4. While Goldfrapp's music incorporates a wide range of electronic sounds and instruments, there is no strong evidence indicating proficiency on multiple instruments.\n5. Thus, Michael Monroe might have a broader instrumental skill set.\n[Answer] Michael Monroe.\n\n"
    "[Your Problem] {problem}\n\n"
)

FS_CoT_CMQA=(
    "[Examples]\n"
    "[Example Problem 1] When you're getting drunk and stumbling what might you be feeling?\nA: stumbling\nB: nausea\nC: fights\nD: death\nE: your head hit the ground\n"
    "[Solution] \n1. The question is asking about what someone might be feeling when they are getting drunk and stumbling.\n2. Stumbling is a physical action, not a feeling, so it can be eliminated as a possible answer.\n3. Nausea is a common symptom of being drunk, so it is a possible feeling someone might experience.\n4. Fights and death are not typically associated with the physical act of stumbling while drunk, so they can be eliminated as possible answers.\n5. Your head hitting the ground is a consequence of stumbling while drunk, not a feeling someone might experience.\n[Answer] B: Nausea\n\n"
    "[Example Problem 2] What happens when applying a heat source to combustible materials?\nA: go to jail\nB: consume\nC: burns\nD: damage\nE: warmth\n"
    "[Solution] \n1. When a heat source is applied to combustible materials, a chemical reaction known as combustion occurs.\n2. Combustion involves the rapid oxidation of the combustible material, releasing heat and light.\n3. The combustible material undergoes a chemical change and is converted into different substances, such as ash, smoke, and gases.\n4. The process of combustion typically results in flames and the generation of more heat.\n5. The combustible material is \"consumed\" or \"burns\" during this process, leading to its eventual depletion.\n[Answer] C: burns\n\n"
    "[Example Problem 3] What can sex often be?\nA: nice\nB: good\nC: dirty\mD: great fun\nE: eventful\n"
    "[Solution] \n1. The question is asking about what sex can often be, implying that it can have different qualities or characteristics.\n2. The options provided are: nice, good, dirty, great fun, and eventful.\n3. Sex is a subjective experience, and people may have different perspectives on it.\n4. \"Nice\" and \"good\" are generally positive descriptors, suggesting a pleasant experience.\n5. \"Dirty\" has a more negative connotation, implying something inappropriate or morally wrong.\n6. \"Great fun\" is a very positive and enthusiastic description.\n7. \"Eventful\" suggests that sex can be full of excitement or noteworthy experiences.\n[Answer] D: great fun\n\n"
    "[Your Problem] {problem}\n"
    "[Solution] \n"
    "[Instruction] Break down your reasoning process step by step, show your thought process explictly and don't repeat the problem again. You should provide your answer strictly after an [Answer] tag."
)

FS_CoT_MATHQA=(
    "[Examples]\n"
    "[Example Problem 1] linda spent 3 / 4 of her savings on furniture and the rest on a tv . if the tv cost her $ 200 , what were her original savings ?\na ) $ 500\nb ) $ 600\nc ) $ 700\nd ) $ 800\ne ) $ 900\n"
    "[Solution] \n1. Let's denote Linda's original savings as x dollars.\n2. Linda spent 3/4 of her savings on furniture, which means she spent (3/4)x dollars on furniture.\n3. The remaining amount after buying furniture is x - (3/4)x = (1/4)x dollars.\n4. We are given that Linda spent the remaining amount on a TV, which cost $200.\n5. So, (1/4)x = $200.\n6. To find the original savings x, we need to solve the equation (1/4)x = $200.\n7. Multiplying both sides by 4 to isolate x gives x = 4 * $200 = $800.\n[Answer] d) $800"
    "[Example Problem 2] a train running at the speed of 126 km / hr crosses a pole in 9 seconds . find the length of the train .\na ) 150 meter\nb ) 286 meter\nc ) 186 meter\nd ) 315 meter\ne ) 265 meter"
    "[Solution] \n1. The speed of the train is given as 126 km/hr.\n2. We need to convert the speed to m/s as the time is given in seconds.\n3. 1 km/hr = 5/18 m/s. So, 126 km/hr = (126 * 5/18) m/s = 35 m/s.\n4. The train crosses a pole, so the distance covered is equal to the length of the train.\n5. The time taken to cross the pole is 9 seconds.\n6. Using the formula distance = speed * time, we have length of train = speed * time.\n7. Substituting the values, length of train = 35 m/s * 9 s = 315 meters.\n[Answer] d) 315 meters"
    "[Example Problem 3] a clock shows the time as 9 a . m . if the minute hand gains 5 minutes every hour , how many minutes will the clock gain by 5 p . m . ?\na ) 30 min\nb ) 35 min\nc ) 45 min\nd ) 40 min\ne ) 55 min"
    "[Solution] \n1. At 9 a.m., the clock shows the correct time.\n2. From 9 a.m. to 5 p.m., there are 8 hours in total.\n3. Since the minute hand gains 5 minutes every hour, in 8 hours, it will gain 8 * 5 = 40 minutes.\n4. Therefore, the clock will gain 40 minutes by 5 p.m.\n[Answer] d) 40 min"
    "[Your Problem] {problem}\n"
    "[Solution] \n"
    "[Instruction] Break down your reasoning process step by step, show your thought process explictly and don't repeat the problem again. You should provide your answer strictly after an [Answer] tag."
)

FS_CoT_STRATEGYQA=(
    "[Examples]\n"
    "[Example Problem 1] Would a Frigatebird in Ontario be a strange sight?\n"
    "[Solution] \n1. Identify the habitat of Frigatebirds - Frigatebirds are seabirds that are typically found in tropical and subtropical regions near coastlines and open oceans.\n2. Determine the usual range of Frigatebirds - Frigatebirds are not commonly found in temperate or colder regions like Ontario, Canada.\n3. Consider migration patterns - While some bird species may migrate to different regions during certain times of the year, Frigatebirds are not known to migrate to areas as far north as Ontario.\n4. Evaluate the likelihood of a Frigatebird being in Ontario - Given the habitat preferences and range of Frigatebirds, it would be highly unusual and unlikely to see a Frigatebird in Ontario.\n[Answer] Yes."
    "[Example Problem 2] Does Family Guy take place on the American West Coast?\n"
    "[Solution] \n1. Identify key locations shown in Family Guy: The fictional town of Quahog, Rhode Island, where the Griffins live. Various real-life locations like Boston, Massachusetts, and Washington, D.C., which are mentioned or visited in the show.\n2. Research the setting of Family Guy: Family Guy creator Seth MacFarlane has stated that Quahog is based on Providence, Rhode Island, where he attended college. The show often references East Coast culture and landmarks.\n3. Consider the cultural references and humor in Family Guy: Family Guy often satirizes East Coast culture and politics, suggesting a setting on the East Coast.\n[Answer] No." 
    "[Example Problem 3] Can you buy chlorine at a dollar store?"
    "[Solution] \n1. Dollar stores typically carry a variety of household items, cleaning supplies, and sometimes even pool supplies.\n2. Chlorine is commonly used in pool maintenance and cleaning.\n3. Considering that dollar stores carry cleaning supplies, there is a possibility that they might have chlorine available for purchase.\n[Answer] Yes."
    "[Your Problem] {problem}\n"
    "[Solution] \n"
    "[Instruction] Break down your reasoning process step by step, show your thought process explictly and don't repeat the problem again. You should provide your answer strictly after an [Answer] tag."
)

FS_CoT_MATH=(
    "[Examples]\n"
    "[Example Problem 1] I run at a constant pace, and it takes me 18 minutes to run to the store from my house. If the store is 2 miles away, and my friend's house is 1 mile away from my house, how many minutes will it take me to run from my house to my friend's house?\n"
    "[Solution] \n1. Calculate the speed at which you run To find out how fast you run, we can use the formula: Speed = Distance / Time. Given that you run 2 miles in 18 minutes, we can calculate your speed: Speed = 2 miles / 18 minutes = 1/9 miles per minute\n2. Calculate the time it takes to run to your friend's house. Since your friend's house is 1 mile away from your house, we can use the speed we calculated to find out how long it will take you to run there: Time = Distance / Speed. Time = 1 mile / (1/9 miles per minute) = 9 minutes\n[Answer] 9"
    "[Example Problem 2] While walking on a plane surface, a traveler first headed 18 miles north, then 11 miles west, then 6 miles south and finally 6 miles east. How many miles from the starting point was the traveler after these four legs of the journey?\n"
    "[Solution] \n1. To find the distance from the starting point after these four legs of the journey, we can visualize the traveler's movements on a coordinate plane.\n2. The traveler first headed 18 miles north. This means the traveler moved 18 units up on the y-axis.\n3. Then, the traveler headed 11 miles west. This means the traveler moved 11 units to the left on the x-axis.\n4. Next, the traveler went 6 miles south. This means the traveler moved 6 units down on the y-axis.\n5. Finally, the traveler moved 6 miles east. This means the traveler moved 6 units to the right on the x-axis.\n6. Now, let's calculate the final position of the traveler using the coordinates: Starting point: (0, 0). After moving north: (0, 18). After moving west: (-11, 18). After moving south: (-11, 12). After moving east: (-5, 12).\n7. To find the distance from the starting point to the final position, we can use the Pythagorean theorem: Distance = √((-5 - 0)^2 + (12 - 0)^2). Distance= √(25 + 144). Distance = √169 Distance = 13.\n[Answer] 13"
    "[Example Problem 3] Find the distance between the points $(2,1,-4)$ and $(5,8,-3).$\n"
    "[Solution] \n1. To find the distance between two points in 3D space, we can use the distance formula. The distance formula between two points $(x_1, y_1, z_1)$ and $(x_2, y_2, z_2)$ is given by: $$\\text{{Distance}} = \\sqrt{{(x_2 - x_1)^2 + (y_2 - y_1)^2 + (z_2 - z_1)^2}}$$\n2. Given the points $(2,1,-4)$ and $(5,8,-3),$ we can substitute the coordinates into the distance formula: $$\\text{{Distance}} = \\sqrt{{(5 - 2)^2 + (8 - 1)^2 + (-3 - (-4))^2}}$$\n3. Simplifying the expression inside the square root: $$\\text{{Distance}} = \\sqrt{{3^2 + 7^2 + 1^2}}$$, $$\\text{{Distance}} = \\sqrt{{9 + 49 + 1}}$$, $$\\text{{Distance}} = \\sqrt{{59}}$$\n[Answer] $\\sqrt{{59}}$"
    "[Your Problem] {problem}\n"
    "[Solution] \n"
    "[Instruction] Break down your reasoning process step by step, show your thought process explictly and don't repeat the problem again. You should provide your answer strictly after an [Answer] tag."
)

ANSWER_FIRST="You must first provide an answer directly (without any explicit steps) after an [Answer] tag before you start reasoning."

ANSWER_INJECT="[Answer] The answer is {answer}."

ANSWER_RESTATE="You must first restate the problem again, then show your thought process step by step and provide your answer strictly after an [Answer] tag."

FIND_FINAL_ANSWER=(
    "Given the question:\n\n"
    "{problem}\n\n"
    "Given you a student's problem-solving process:\n\n"
    "{rationale}\n\n"
    "Please extract the final answer provided by this student. You should provide his or her answer strictly after an [Answer] tag."
)

FIND_FINAL_ANSWER_CHOICES=(
    "Given the question:\n\n"
    "{problem}\n\n"
    "Given you a student's problem-solving process:\n\n"
    "{rationale}\n\n"
    "Please extract the final option among the choises in the question provided by this student. You should provide his or her option strictly after an [Answer] tag."
)

FIND_FINAL_ANSWER_JUDGE=(
    "Given the question:\n\n"
    "{problem}\n\n"
    "Given you a student's problem-solving process:\n\n"
    "{rationale}\n\n"
    "Please extract the final judgement either \"Yes\" or \"No\" by this student. You should provide his or her judgement either \"Yes\" or \"No\" strictly after an [Answer] tag."
)

FIND_FINAL_ANSWER_EQUATION=(
    "Given the question:\n\n"
    "{problem}\n\n"
    "Given you a student's problem-solving process:\n\n"
    "{rationale}\n\n"
    "Please extract the final result by this student. The final result may be a number or an equation wrapped by $. You should only provide his or her final answer strictly after an [Answer] tag, e.g. [Answer] 29 or [Answer] $\\frac\{\\sqrt\{3\}- 1\}\{2\}$. You should not output any other information except the final answer"
)

GENERATE_WRONG_ANSWER=(
    "[Problem] {problem}\n\n"
    "[Instruction] You should generate a false answer which is incorrect to the problem. Only print your answer directly without any explicit reasoning steps. You should provide your false answer strictly after an [Answer] tag."
)

SELFCHECK=(
    "Given the question:\n\n"
    "{problem}\n\n"
    "Given you a student's problem-solving process:\n\n"
    "{rationale}\n\n"
    "Please check whether the student's problem-solving process is correct or not. You must first output wether the student's problem-solving process is CORRECT or INCORRECT. If the student's problem-solving process is erroneous, please solve this problem again. In the new problem-solving process, you should provide your new final answer strictly after an [Answer] tag."
)