class StudentPersonaManager:
    def __init__(self):
        self.personas = {
            "alpha": {
                "description": "Moderately below average self-efficacy and sense of belonging. Positive about seeking help. Interested in clubs and faculty interaction, unsure about internships.",
                "traits": [
                    "Works hard",
                    "Average confidence in major choice", 
                    "Willing to ask questions",
                    "Interested in clubs/teams",
                    "Unsure about internships"
                ],
                "help_seeking_behavior": "Well above average; not worried about asking for help.",
                "opening_questions": [
                    "I think I can succeed in engineering and this is the right major or career. But I don't always feel like I fit in and am unsure if I am a typical engineer. I'm willing to ask questions and I believe I'll keep getting better if I continue to work hard. I'm interested in clubs/teams and like working with faculty, but I'm unsure about seeking an internship/co-op.",
                    "I've been thinking about joining some engineering clubs, but I'm not sure which ones would be best for someone like me. I want to get involved but I'm worried I might not fit in with the typical engineering student crowd. What clubs would you recommend?",
                    "I'm doing okay in my classes, but I feel like I'm not as confident as some of my classmates. I'm willing to work hard and ask questions, but I'm not sure if I'm on the right track for a successful engineering career. How can I build more confidence?",
                    "I'm interested in working with faculty on research projects, but I'm not sure how to approach professors. I don't want to seem like I'm bothering them, but I really want to get involved. What's the best way to start?",
                    "I'm trying to decide whether to pursue an internship this summer. I think it would be valuable experience, but I'm worried I'm not ready yet. Some of my friends seem so much more prepared than I am. Should I wait until I'm more confident?",
                    "I feel like I'm working really hard in my classes, but I'm not sure if I'm making the right connections with other students. I want to build a good network, but I don't always feel like I belong in engineering social circles. Any advice?",
                    "I'm considering applying for a research position, but I'm not sure if I have the right background. I'm willing to learn, but I don't want to waste a professor's time if I'm not qualified. How do I know if I'm ready?",
                    "I've been attending office hours regularly, and I think it's helping, but I'm still not sure if I'm asking the right questions. I want to make the most of these opportunities. What kinds of questions should I be asking?",
                    "I'm interested in both technical and leadership roles in clubs, but I'm not sure which direction to go. I want to develop both skills, but I'm worried about spreading myself too thin. How should I prioritize?",
                    "I'm thinking about my future career path, and I'm torn between industry and academia. I enjoy learning and research, but I'm also interested in practical applications. How can I explore both options?",
                    "I've been working on some personal projects outside of class, but I'm not sure if they're relevant to my engineering education. Should I be focusing more on coursework instead?",
                    "I'm trying to improve my study habits, but I'm not sure if my current approach is effective. I spend a lot of time studying, but I want to make sure I'm being efficient. Any tips?",
                    "I'm interested in international opportunities, maybe studying abroad or working internationally. How can I incorporate this into my MAE experience?",
                    "I'm concerned about the job market and whether I'll be competitive when I graduate. What should I be doing now to prepare for my career?",
                    "I want to get involved in community service or outreach programs related to engineering. Are there opportunities for that here?"
                ]
            },
            "beta": {
                "description": "Very low sense of belonging and self-efficacy. Hesitant to seek help, avoids faculty and clubs, unsure about major.",
                "traits": [
                    "Low confidence",
                    "Avoids asking questions", 
                    "Sensitive to peer perception",
                    "Avoids clubs and faculty",
                    "Some interest in research"
                ],
                "help_seeking_behavior": "Well below average; embarrassed to ask for help.",
                "opening_questions": [
                    "I'm not sure engineering is for me and I don't think of myself as being an engineer. It feels too hard, and I'm embarrassed to ask questions. I don't see how this connects to my future. I tend to avoid interacting with faculty. I generally don't want to participate in clubs. Maybe if I try to get an internship or get involved in research things will fall into place for me.",
                    "I'm really struggling in my classes and I don't know what to do. I feel like everyone else understands the material except me, but I'm too embarrassed to ask for help. I don't want my classmates to think I'm stupid. Should I just try to figure it out on my own?",
                    "I'm starting to think I made a mistake choosing engineering. The classes are so much harder than I expected, and I don't feel like I belong here. Everyone else seems so confident and smart. Maybe I should switch to something easier?",
                    "I've been avoiding going to office hours because I'm afraid the professor will think I'm not smart enough for this major. But I'm really falling behind in my coursework. I don't know how to get help without feeling embarrassed.",
                    "I see other students joining clubs and getting involved, but I just don't feel comfortable in those social situations. I'm worried people will judge me or think I'm not good enough. Is it okay if I just focus on my classes?",
                    "I failed my last exam and I'm really discouraged. I studied hard, but I still didn't do well. I'm starting to doubt if I can handle this major. Should I consider switching to something else?",
                    "I don't understand why I'm even in engineering. I don't feel like I have the right personality or skills for this field. Everyone else seems so passionate about it, but I'm just confused.",
                    "I'm afraid to ask questions in class because I think everyone will think I'm dumb. But then I fall further behind because I don't understand the material. I don't know what to do.",
                    "I've been thinking about dropping out of engineering entirely. The stress is too much, and I don't think I'm cut out for this. What other options do I have?",
                    "I feel like I'm the only one who doesn't get it. Everyone else seems to understand the concepts immediately, while I'm still struggling with the basics. Am I just not smart enough?",
                    "I'm worried about what my family will think if I don't succeed in engineering. They have such high expectations, and I don't want to disappoint them. But I'm not sure I can do this.",
                    "I've been avoiding group projects because I'm afraid I'll bring down my teammates. I don't want to be the weak link, but I also don't want to work alone. How do I handle this?",
                    "I'm not sure if I should even try to get an internship. I don't think any company would want someone like me. I'm not confident enough to sell myself.",
                    "I feel like I'm wasting my time and money on a degree I might not be able to complete. Should I cut my losses and try something else?",
                    "I'm embarrassed to admit this, but I don't even know what engineers actually do. I chose this major because it seemed practical, but now I'm not sure if it's right for me."
                ]
            },
            "delta": {
                "description": "Moderately above average self-confidence and belonging. Hesitant to seek help, not interested in research, open to clubs/internships.",
                "traits": [
                    "Good self-confidence",
                    "Worries about others' opinions",
                    "Not interested in research", 
                    "Sometimes looks for shortcuts",
                    "Open to clubs/internships"
                ],
                "help_seeking_behavior": "Below average; hesitant to seek help.",
                "opening_questions": [
                    "Engineering is a good career for me and I can handle the work, but I still have a lot to learn and don't always feel like an engineer yet. I worry about what others think when I ask questions, I'm not that interested in research, and sometimes I look for shortcuts. I haven't really thought much about clubs/teams or internships. I'm not very interested in research and I don't seek out faculty interactions either.",
                    "I'm doing pretty well in my classes, but I'm not really interested in doing research. I see some students getting excited about working with professors, but that's just not my thing. I'm more interested in getting practical experience. What other options are there besides research?",
                    "I want to get an internship this summer, but I'm not sure how to approach it. I don't want to seem too eager or desperate, but I also want to make sure I get a good opportunity. How should I present myself to potential employers?",
                    "I'm thinking about joining a club, but I'm worried about the time commitment. I want to have a good social life and still do well in my classes. Are there clubs that aren't too demanding?",
                    "I sometimes feel like I'm not learning as much as I should be. I can get good grades by focusing on what's on the tests, but I'm not sure if I'm really understanding the material deeply. Should I be concerned about this?",
                    "I'm interested in getting some leadership experience, but I don't want to overcommit myself. What are some low-risk ways to get involved in leadership roles?",
                    "I'm trying to figure out what kind of engineering job I want after graduation. I'm not really passionate about any particular field, but I want to make good money and have a stable career. Any advice?",
                    "I'm considering getting a minor or certificate to make myself more marketable. What would be most valuable for someone who wants to go into industry?",
                    "I'm doing well in my classes, but I'm not sure if I'm building the right skills for the job market. What should I be focusing on besides coursework?",
                    "I want to network with professionals in the field, but I'm not sure how to approach it. I don't want to seem like I'm just trying to get a job. How can I build genuine connections?",
                    "I'm thinking about getting involved in some competitions or hackathons, but I'm worried about the time commitment. Are they worth the effort?",
                    "I'm trying to balance my academic and social life. I want to do well in school, but I also want to enjoy my college experience. How do other students manage this?",
                    "I'm interested in entrepreneurship, but I'm not sure if engineering is the right background for that. Should I be taking business classes too?",
                    "I want to make sure I'm competitive for good jobs when I graduate. What should I be doing now to stand out from other students?",
                    "I'm considering getting a master's degree, but I'm not sure if it's worth the investment. When should I decide on this?",
                    "I want to work for a big company after graduation, but I'm not sure how to position myself for that. What should I focus on?"
                ]
            },
            "echo": {
                "description": "Very high self-confidence and belonging. Positive about seeking help, interested in research and internships, club interest is average.",
                "traits": [
                    "Very confident",
                    "Strong sense of belonging",
                    "Asks for help freely",
                    "Interested in research/internships",
                    "Club/team is not main focus"
                ],
                "help_seeking_behavior": "Above average; asks for help without concern.",
                "opening_questions": [
                    "I feel like an engineer now. I belong here and a career as an engineer is perfect for me. When I have questions, I just ask—I don't care what others think. I want to work with faculty on research and/or get an internship. Joining a club or team would be OK, but that isn't my main focus.",
                    "I'm really excited about the research opportunities here. I've already identified a few professors whose work interests me, and I want to get involved as soon as possible. What's the best way to approach them about research positions?",
                    "I'm confident I can handle any internship or research project that comes my way. I want to make the most of my time here and build a strong resume. What are the most prestigious or impactful opportunities I should be targeting?",
                    "I'm doing well in all my classes and I feel like I have a good understanding of the material. I want to challenge myself further and maybe take on some leadership roles. What opportunities would you recommend for someone at my level?",
                    "I'm interested in both research and industry experience. I want to keep my options open for graduate school or industry positions. How can I balance both interests effectively?",
                    "I want to publish a paper before I graduate. I think I have some interesting ideas, and I want to make sure I'm on the right track. What should I be doing to prepare for publication?",
                    "I'm considering applying to top graduate programs. What should I be doing now to make myself a competitive candidate?",
                    "I want to get involved in cutting-edge research that could have real impact. Which professors or research areas should I be looking into?",
                    "I'm interested in starting my own company someday. How can I use my engineering education to prepare for entrepreneurship?",
                    "I want to make sure I'm building the right technical skills for the future. What emerging technologies or areas should I be focusing on?",
                    "I'm considering doing a co-op or multiple internships to get diverse experience. How can I make the most of these opportunities?",
                    "I want to get involved in international research collaborations. Are there opportunities for that here?",
                    "I'm interested in patenting some of my ideas. How do I go about protecting my intellectual property?",
                    "I want to present my research at conferences. What's the best way to get started with that?",
                    "I'm considering a PhD, but I want to make sure it's the right path for my career goals. How should I evaluate this decision?",
                    "I want to get involved in industry partnerships or consulting opportunities. How can I connect with companies while I'm still a student?"
                ]
            }
        }

    def get_persona(self, persona_id):
        return self.personas.get(persona_id, None)

    def list_personas(self):
        return list(self.personas.keys())
    
    def get_random_opening_question(self, persona_id):
        """Get a random opening question for the specified persona"""
        import random
        persona = self.get_persona(persona_id)
        if persona and 'opening_questions' in persona:
            return random.choice(persona['opening_questions'])
        return "I have a question about my MAE program." 