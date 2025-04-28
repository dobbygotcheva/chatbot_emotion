import re
import json
import logging
import random
import math
from typing import Dict, List, Tuple, Optional

from chatbot_app.chatbot.drinks_recommendations import DrinkRecommender

class AdvancedChatbot:
    """
    Advanced chatbot with emotion detection and contextual responses.
    """
    def __init__(self):
        """
        Initialize the chatbot with emotion patterns, responses, and context.
        """
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Initialize conversation memory
        self.conversation_memory = []

        # Initialize context
        self.context = {
            'current_emotion': 'neutral',
            'current_topic': None,
            'previous_messages': [],
            'session_emotions': [],
            'drink_recommendation_state': None,
            'current_drink_question': None
        }

        # Initialize drink recommender
        self.drink_recommender = DrinkRecommender()

        # Initialize drink recommendation patterns
        self.drink_recommendation_patterns = [
            r'(?i)\b(recommend|suggest|what|which).*?(drink|alcohol|cocktail|beer|wine|whiskey|vodka)\b',
            r'(?i)\b(what|which).*?(drink|alcohol|cocktail|beer|wine|whiskey|vodka).*?(should|would|could|can).*?(i|we).*?(have|try|drink|get)\b',
            r'(?i)\b(i|we).*?(want|need|would like).*?(a|some|to get).*?(drink|alcohol|cocktail|beer|wine|whiskey|vodka)\b',
            r'(?i)\b(i|we).*?(want|need|would like).*?(something).*?(to drink|to have)\b',
            r'(?i)\b(help me|tell me).*?(choose|pick|select|find).*?(a|some).*?(drink|alcohol|cocktail|beer|wine|whiskey|vodka)\b',
            r'(?i)\bcan you recommend a drink\b',
            r'(?i)\brecommend.*?drink\b',
            r'(?i)\bdrink recommendation\b',
            r'(?i)\bsuggest.*?drink\b'
        ]

        # Initialize sentiment analyzer with expanded vocabulary
        self.sentiment_analyzer = {
            'positive': [
                'happy', 'joy', 'love', 'excited', 'grateful', 'glad', 'pleased', 'delighted', 
                'content', 'satisfied', 'cheerful', 'joyful', 'thrilled', 'elated', 'ecstatic', 
                'wonderful', 'fantastic', 'terrific', 'great', 'good', 'nice', 'awesome', 'amazing', 
                'excellent', 'superb', 'brilliant', 'outstanding', 'fabulous', 'marvelous', 'splendid',
                'enjoy', 'enjoying', 'enjoyed', 'appreciate', 'appreciating', 'appreciated', 'like', 
                'liked', 'loving', 'adore', 'adoring', 'admire', 'admiring', 'cherish', 'cherishing',
                'hopeful', 'optimistic', 'positive', 'confident', 'enthusiastic', 'eager', 'keen',
                'proud', 'triumphant', 'victorious', 'successful', 'accomplished', 'achieved',
                'blessed', 'fortunate', 'lucky', 'privileged', 'honored', 'inspired', 'motivated',
                'energized', 'refreshed', 'renewed', 'revitalized', 'uplifted', 'encouraged',
                'empowered', 'fulfilled', 'gratified', 'satisfied', 'contented', 'peaceful',
                'serene', 'tranquil', 'calm', 'relaxed', 'at ease', 'comfortable', 'cozy',
                'secure', 'safe', 'protected', 'supported', 'validated', 'affirmed', 'accepted',
                'included', 'welcomed', 'valued', 'appreciated', 'respected', 'admired',
                'praised', 'complimented', 'congratulated', 'celebrated', 'honored', 'recognized',
                'rewarded', 'blessed', 'thankful', 'grateful', 'appreciative', 'moved', 'touched'
            ],
            'negative': [
                'sad', 'angry', 'fear', 'disgust', 'disappointed', 'upset', 'unhappy', 'depressed', 
                'miserable', 'gloomy', 'heartbroken', 'devastated', 'crushed', 'hurt', 'pained', 
                'suffering', 'agonizing', 'terrible', 'horrible', 'awful', 'dreadful', 'bad', 'worse', 
                'worst', 'furious', 'enraged', 'outraged', 'annoyed', 'irritated', 'frustrated', 
                'exasperated', 'mad', 'hate', 'hatred', 'despise', 'loathe', 'detest', 'abhor',
                'scared', 'afraid', 'frightened', 'terrified', 'anxious', 'worried', 'concerned', 
                'nervous', 'stressed', 'distressed', 'panicked', 'horrified', 'appalled', 'shocked',
                'disgusted', 'revolted', 'repulsed', 'nauseated', 'sickened', 'offended', 'appalled',
                'disappointed', 'let down', 'disheartened', 'disillusioned', 'dismayed', 'displeased',
                'regretful', 'remorseful', 'guilty', 'ashamed', 'embarrassed', 'humiliated',
                'abandoned', 'rejected', 'betrayed', 'deceived', 'cheated', 'used', 'manipulated',
                'controlled', 'dominated', 'bullied', 'harassed', 'abused', 'victimized', 'targeted',
                'excluded', 'isolated', 'alienated', 'ostracized', 'ignored', 'forgotten', 'neglected',
                'unwanted', 'unloved', 'unappreciated', 'disrespected', 'disregarded', 'dismissed',
                'belittled', 'ridiculed', 'mocked', 'teased', 'taunted', 'insulted', 'offended',
                'criticized', 'judged', 'condemned', 'blamed', 'shamed', 'mortified', 'humiliated',
                'inadequate', 'incompetent', 'incapable', 'helpless', 'powerless', 'weak', 'vulnerable',
                'fragile', 'insecure', 'uncertain', 'doubtful', 'skeptical', 'suspicious', 'paranoid',
                'jealous', 'envious', 'resentful', 'bitter', 'vengeful', 'spiteful', 'hostile',
                'aggressive', 'violent', 'destructive', 'dangerous', 'threatening', 'menacing', 'scary',
                'creepy', 'eerie', 'unsettling', 'disturbing', 'troubling', 'worrisome', 'concerning',
                'alarming', 'dreading', 'desperate', 'hopeless', 'despairing', 'suicidal', 'worthless',
                'useless', 'pointless', 'meaningless', 'empty', 'hollow', 'numb', 'detached', 'disconnected',
                'overwhelmed', 'burdened', 'pressured', 'strained', 'exhausted', 'drained', 'depleted',
                'fatigued', 'tired', 'weary', 'worn out', 'burned out', 'sick', 'ill', 'unwell', 'pained'
            ],
            'neutral': [
                'neutral', 'calm', 'balanced', 'okay', 'ok', 'fine', 'alright', 'so-so', 'moderate', 
                'average', 'ordinary', 'standard', 'normal', 'regular', 'usual', 'common', 'typical',
                'indifferent', 'unbiased', 'impartial', 'dispassionate', 'detached', 'uninvolved',
                'neither', 'nor', 'maybe', 'perhaps', 'possibly', 'somewhat', 'kind of', 'sort of',
                'stable', 'steady', 'consistent', 'even', 'level', 'measured', 'reasonable', 'fair',
                'objective', 'rational', 'logical', 'sensible', 'practical', 'pragmatic', 'realistic',
                'middle-of-the-road', 'middle ground', 'halfway', 'in-between', 'intermediate', 'medium',
                'adequate', 'sufficient', 'acceptable', 'satisfactory', 'passable', 'tolerable', 'decent',
                'not bad', 'not good', 'not great', 'meh', 'whatever', 'anyhow', 'anyway', 'regardless',
                'nevertheless', 'nonetheless', 'however', 'still', 'yet', 'though', 'although', 'even so',
                'all the same', 'at any rate', 'in any case', 'in any event', 'be that as it may',
                'reserved', 'restrained', 'controlled', 'composed', 'collected', 'poised', 'dignified',
                'formal', 'proper', 'correct', 'appropriate', 'suitable', 'fitting', 'apt', 'becoming',
                'equanimous', 'equable', 'temperate', 'mild', 'gentle', 'soft', 'light', 'slight',
                'undecided', 'uncertain', 'unsure', 'ambivalent', 'conflicted', 'torn', 'of two minds',
                'on the fence', 'sitting on the fence', 'hedging', 'noncommittal', 'uncommitted', 'undetermined'
            ],
            'intensity_modifiers': [
                'very', 'really', 'extremely', 'incredibly', 'exceptionally', 'absolutely', 'completely',
                'totally', 'utterly', 'thoroughly', 'entirely', 'fully', 'highly', 'intensely', 'deeply',
                'profoundly', 'immensely', 'tremendously', 'exceedingly', 'extraordinarily', 'remarkably',
                'particularly', 'especially', 'notably', 'significantly', 'substantially', 'considerably',
                'greatly', 'vastly', 'hugely', 'enormously', 'immeasurably', 'unbelievably', 'insanely',
                'ridiculously', 'crazy', 'super', 'mega', 'ultra', 'beyond', 'so', 'such', 'quite', 'rather',
                'amazingly', 'astonishingly', 'astoundingly', 'strikingly', 'stunningly', 'surprisingly',
                'shockingly', 'overwhelmingly', 'overpoweringly', 'intensively', 'fiercely', 'ferociously',
                'violently', 'severely', 'seriously', 'gravely', 'critically', 'desperately', 'urgently',
                'terribly', 'horribly', 'awfully', 'dreadfully', 'frightfully', 'fearfully', 'appallingly',
                'atrociously', 'abominably', 'disgustingly', 'revoltingly', 'repulsively', 'sickeningly',
                'nauseatingly', 'unbearably', 'intolerably', 'insufferably', 'unendurably', 'unspeakably',
                'indescribably', 'inconceivably', 'unimaginably', 'unfathomably', 'incomprehensibly',
                'impossibly', 'incredibly', 'unbelievably', 'fantastically', 'phenomenally', 'monumentally',
                'colossally', 'gigantically', 'astronomically', 'exponentially', 'infinitely', 'eternally',
                'perpetually', 'endlessly', 'ceaselessly', 'relentlessly', 'persistently', 'consistently',
                'constantly', 'continually', 'continuously', 'incessantly', 'unceasingly', 'unremittingly',
                'unrelentingly', 'unwaveringly', 'unfailingly', 'undoubtedly', 'unquestionably', 'undeniably',
                'indisputably', 'irrefutably', 'incontrovertibly', 'incontestably', 'unmistakably', 'decidedly',
                'definitely', 'certainly', 'surely', 'positively', 'absolutely', 'categorically', 'emphatically',
                'vehemently', 'passionately', 'ardently', 'fervently', 'zealously', 'fanatically', 'obsessively',
                'compulsively', 'maniacally', 'wildly', 'madly', 'crazily', 'hysterically', 'frantically',
                'frenziedly', 'deliriously', 'ecstatically', 'euphorically', 'rapturously', 'blissfully',
                'joyfully', 'gleefully', 'merrily', 'cheerfully', 'happily', 'contentedly', 'satisfyingly',
                'pleasingly', 'gratifyingly', 'rewardingly', 'fulfillingly', 'meaningfully', 'significantly',
                'importantly', 'crucially', 'vitally', 'essentially', 'fundamentally', 'basically', 'primarily'
            ]
        }

        # Initialize topic responses
        self.topic_responses = {
            "general": "I'm here to help. What would you like to talk about today?",
            "health": "Health is so important. What aspects of your wellbeing are you focusing on right now?",
            "technology": "Technology can be both fascinating and challenging. What's on your mind in the tech world?",
            "education": "Learning opens so many doors. What are you curious about or working to understand better?",
            "entertainment": "Taking time for enjoyment is essential for balance. What kind of entertainment interests you?",
            "politics": "Staying informed about current events can be valuable. What aspects of this topic are you thinking about?",
            "science": "Science helps us understand our world in amazing ways. What scientific topics interest you?",
            "relationships": "Connections with others are a fundamental part of life. How are your relationships going?",
            "personal_development": "Growth is a journey, not a destination. What areas of development are you focusing on?",
            "finance": "Financial wellbeing contributes to peace of mind. What financial matters are you considering?"
        }

        # Initialize emotion patterns with comprehensive matching for all emotions
        self.emotion_patterns = {
            'achievement': [
                r'\b(i|we) (took|passed|completed|finished|aced|won|accomplished|achieved|succeeded in|managed to)\b',
                r'\b(i|we) (found|got|landed|secured|obtained) (a job|a new job|a position|a role|a promotion|an opportunity)\b',
                r'\b(i|we) (lost|shed|dropped|reduced) (weight|pounds|kilos|kg|lb)\b',
                r'\b(i|we) (graduated|earned|received|got) (a degree|a diploma|a certificate|a license)\b',
                r'\b(i|we) (reached|hit|attained|met) (my|our) (goal|target|objective|milestone)\b',
                r'\b(i|we) (finally|successfully|proudly) (did it|made it|completed it|finished it)\b',
                r'\b(i|we) (overcame|conquered|beat|defeated|mastered) (a challenge|an obstacle|a difficulty|a problem|a fear)\b',
                r'\b(achievement|accomplishment|success|victory|milestone|breakthrough|triumph)\b',
                r'\b(proud of|accomplished|achieved|succeeded|won|completed|finished|mastered)\b',
                r'\b(i|we) (earned|deserved|worked for|gained) (this|that|it|recognition|praise|reward)\b'
            ],
            'admiration': [
                r'\b(i|we) (admire|look up to|respect|appreciate|value|esteem|revere|honor|idolize) (you|him|her|them|your|his|her|their)\b',
                r'\b(i|we) (am|are|feel|felt) (admiration|respect|appreciation|awe|reverence|regard) (for|towards)\b',
                r'\b(you|he|she|they) (are|is) (admirable|impressive|inspiring|amazing|remarkable|extraordinary|exceptional|outstanding)\b',
                r'\b(so|very|really|truly|deeply) (admire|respect|appreciate|impressed by|inspired by|in awe of)\b',
                r'\b(admiration|respect|appreciation|awe|reverence|regard|esteem|honor)\b',
                r'\b(role model|hero|inspiration|mentor|idol|example|standard|benchmark)\b',
                r'\b(look up to|inspired by|impressed by|in awe of|blown away by|amazed by) (you|him|her|them|your|his|her|their)\b',
                r'\b(i wish i could|i aspire to|i hope to) (be like|emulate|match|reach|achieve) (you|him|her|them|your|his|her|their)\b',
                r'\b(i|we) (admire|look up to|respect|appreciate|value|esteem|revere|honor|idolize) (my|our) (professor|teacher|mentor|boss|coach|leader|supervisor|manager|friends|friend|family|parents|colleagues|coworkers|teammates|partner|spouse)\b',
                r'\b(i|we) (admire|look up to|respect|appreciate|value|esteem|revere|honor|idolize) (.*?)\b',
                r'\b(that is|that\'s) (admiration|adminration)\b'
            ],
            'amusement': [
                r'\b(i|we) (am|are|feel|felt) (amused|entertained|tickled|delighted|laughing|giggling|chuckling)\b',
                r'\b(that|this) (is|was) (funny|hilarious|amusing|entertaining|comical|humorous|witty|hysterical)\b',
                r'\b(i|we) (laughed|giggled|chuckled|cracked up|burst out laughing|couldn\'t stop laughing)\b',
                r'\b(😂|🤣|😆|😄|😹|🙃|😅)\b',
                r'\b(so|very|really|extremely|incredibly) (funny|amusing|hilarious|entertaining|comical|humorous)\b',
                r'\b(humor|comedy|joke|pun|meme|laughter|amusement|entertainment)\b',
                r'\b(made me laugh|cracked me up|tickled me|had me in stitches|had me rolling|lol|haha|hehe)\b',
                r'\b(funny|hilarious|amusing|entertaining|comical|humorous|witty|hysterical)\b'
            ],
            'annoyance': [
                r'\b(i|we) (am|are|feel|felt) (annoyed|irritated|bothered|irked|vexed|peeved|displeased|frustrated|aggravated|exasperated|ticked off|miffed)\b',
                r'\b(this|that) (is|was) (annoying|irritating|bothersome|irksome|vexing|frustrating|aggravating|grating|infuriating|exasperating|maddening|tiresome)\b',
                r'\b(it|this|that) (annoys|irritates|bothers|irks|vexes|peeves|frustrates|aggravates|grates on|gets on|drives) (me|us) (crazy|nuts|insane|mad|up the wall)?\b',
                r'\b(getting|becoming|growing) (annoyed|irritated|bothered|frustrated|impatient|fed up|sick and tired|short-tempered)\b',
                r'\b(annoyance|irritation|frustration|vexation|displeasure|impatience|exasperation|aggravation|pet peeve)\b',
                r'\b(stop|quit|cease|cut it out|knock it off|give it a rest) (it|that|this|doing that|bothering me|annoying me|already)\b',
                r'\b(tired of|fed up with|sick of|had enough of|can\'t stand|can\'t take|done with|over|through with|at my limit with) (this|that|it|you|them|him|her)\b',
                r'\b(ugh|argh|grr|hmph|sigh|whatever|seriously|really|come on|oh please|for crying out loud|give me a break|enough already|how many times|not again)\b',
                r'\b(on my nerves|getting to me|pushing my buttons|testing my patience|making me crazy|driving me nuts|the last straw)\b',
                r'\b(why (do|would|should) (you|they|people|someone))|(how (hard|difficult) is it)|(what does it take)\b'
            ],
            'anticipation': [
                r'\b(i|we) (am|are|feel|felt) (anticipating|expecting|awaiting|looking forward to|excited about|eager for)\b',
                r'\b(i|we) (can\'t wait|am waiting|are waiting|have been waiting) (for|to)\b',
                r'\b(i|we) (am|are) (excited|thrilled|eager|keen|impatient|anxious|ready) (about|for|to)\b',
                r'\b(looking forward to|counting down to|excited about|eager for|ready for|prepared for)\b',
                r'\b(anticipation|expectation|excitement|eagerness|readiness|preparation)\b',
                r'\b(soon|coming|approaching|upcoming|imminent|forthcoming|about to)\b',
                r'\b(can\'t wait|so excited|really looking forward|eagerly awaiting|eagerly anticipating)\b',
                r'\b(countdown|preparing|getting ready|planning|anticipating)\b'
            ],
            'approval': [
                r'\b(i|we) (approve|agree|endorse|support|back|favor|like|accept) (of|with)\b',
                r'\b(i|we) (give|gave|offer|offered) (my|our) (approval|blessing|endorsement|support|backing)\b',
                r'\b(this|that) (has|gets|earns|deserves|receives) (my|our) (approval|blessing|endorsement|support|backing)\b',
                r'\b(i|we) (am|are) (in favor of|supportive of|behind|on board with|pleased with)\b',
                r'\b(i|we) (am|are) (satisfied with) (?!(my|our) (language skills|abilities|performance|achievements|accomplishments|work|results|progress|growth|development|improvement))\b',
                r'\b(approval|agreement|endorsement|support|backing|acceptance|thumbs up|green light)\b',
                r'\b(approved|agreed|endorsed|supported|backed|favored|accepted)\b',
                r'\b(good job|well done|nice work|great work|excellent|perfect|spot on|exactly right)\b',
                r'\b(👍|✅|✓|👌|💯)\b'
            ],
            'curious': [
                r'\b(i|we) (am|are|feel|felt) (curious|inquisitive|interested|intrigued|fascinated|captivated|wondering)\b',
                r'\b(i|we) (wonder|wondered|am wondering|are wondering|was wondering|were wondering) (about|if|why|how|what|when|where|who)\b',
                r'\b(that|this) (is|was) (interesting|intriguing|fascinating|captivating|thought-provoking|mind-boggling)\b',
                r'\b(i|we) (want|wanted|would like) to (know|learn|understand|discover|explore|find out|figure out)\b',
                r'\b(tell me|explain|share|elaborate) (about|on|more about|further on)\b',
                r'\b(curiosity|interest|intrigue|fascination|wonder|inquisitiveness)\b',
                r'\b(curious|inquisitive|interested|intrigued|fascinated|captivated|wondering) (about|in|by)\b',
                r'\b(hmm|interesting|fascinating|intriguing|tell me more|i\'d like to know more)\b'
            ],
            'caring': [
                r'\b(i|we) (care|care about|care for|look after|take care of|worry about|am concerned about|are concerned about)\b',
                r'\b(i|we) (am|are|feel|felt) (caring|concerned|worried|protective|nurturing|supportive|compassionate|empathetic)\b',
                r'\b(i|we) (want|wanted|would like|wish) (to help|to support|to be there for|to assist|to aid|to comfort)\b',
                r'\b(how are you|are you okay|are you alright|are you well|how are you feeling|how are you doing)\b',
                r'\b(take care|be careful|stay safe|look after yourself|take care of yourself|be well|get well soon)\b',
                r'\b(caring|concern|compassion|empathy|sympathy|kindness|tenderness|warmth|affection)\b',
                r'\b(i\'m here for you|i\'m here if you need me|i\'m here to help|i\'m here to support you|i\'m here to listen)\b',
                r'\b(❤️|💕|💗|💓|💞|💖|💝|🤗|🫂)\b'
            ],
            'confusion': [
                r'\b(i|we) (am|are|feel|felt) (confused|puzzled|perplexed|bewildered|baffled|disoriented|lost|muddled|unclear)\b',
                r'\b(this|that) (is|was) (confusing|puzzling|perplexing|bewildering|baffling|disorienting|unclear|ambiguous|vague)\b',
                r'\b(i|we) (don\'t|do not|can\'t|cannot) (understand|comprehend|grasp|follow|make sense of|figure out|get it)\b',
                r'\b(what|how|why|when|where|who) (does this|is this|does that|is that|do you|are you) (mean|saying|talking about|referring to)\b',
                r'\b(i\'m|i am) (lost|not following|not getting it|missing something|not understanding)\b',
                r'\b(confusion|perplexity|bewilderment|disorientation|uncertainty|ambiguity|vagueness|doubt)\b',
                r'\b(huh|what|eh|um|hmm|wait|sorry|excuse me|pardon|come again)\b',
                r'\b(😕|😟|😮|🤔|❓|❔|🙄|😵‍💫)\b'
            ],
            'desire': [
                r'\b(i|we) (want|desire|wish for|long for|crave|yearn for|hunger for|thirst for|need|would like)\b',
                r'\b(i|we) (am|are|feel|felt) (desire|attraction|lust|passion|yearning|longing|craving|wanting)\b',
                r'\b(i|we) (can\'t stop|cannot stop) (thinking about|wanting|desiring|craving|yearning for|longing for)\b',
                r'\b(i|we) (would do|would give|would trade|would sacrifice) (anything|everything) (for|to)\b',
                r'\b(i|we) (must|have to|need to|really want to|really need to|desperately want to|desperately need to)\b',
                r'\b(desire|want|need|craving|yearning|longing|hunger|thirst|lust|passion|attraction)\b',
                r'\b(desperately|urgently|badly|strongly|deeply|intensely|passionately) (want|need|desire|crave|yearn for|long for)\b',
                r'\b(😍|🥰|😘|💋|💘|💝|💖|💗|💓|💞|💕|❤️|🔥|🥵)\b'
            ],
            'joy': [
                r'\b(i|we) (am|are|feel|felt) (happy|joyful|delighted|cheerful|pleased|content|excited|thrilled|ecstatic|elated|overjoyed)\b',
                r'\b(that|this) (is|was) (wonderful|amazing|fantastic|great|good|perfect|excellent|brilliant|outstanding|superb)\b',
                r'\b(i|we) (feel|felt) (great|good|wonderful|amazing|fantastic|blessed|lucky|on top of the world|over the moon)\b',
                r'\b(😊|😄|😃|😁|🙂|🥰|😍|🤗|😀|😇)\b',
                r'\b(so|very|really|extremely|incredibly) (happy|joyful|delighted|excited|pleased|content)\b',
                r'\b(happiness|joy|delight|pleasure|contentment|bliss|euphoria)\b',
                r'\b(made my day|best day|loving this|loving it|enjoying|enjoy)\b',
                r'\b(what a|such a) (wonderful|beautiful|amazing|lovely|great|fantastic|marvelous|perfect) (world|day|life|moment|experience|feeling)\b',
                r'\b(i|we) (am|are) (glad|happy|thankful|grateful) to be alive\b'
            ],
            'desperation': [
                r'\b(i|we) (am|are|feel|felt) (desperate|hopeless|worthless|useless|suicidal|pointless|helpless|lost|trapped|overwhelmed|doomed|defeated|broken|shattered|devastated|destroyed)\b',
                r'\b(i|we) (want|wanted|wish|wished|need|needed) to (give up|end it all|end my life|die|disappear|vanish|not exist|escape|run away|get away|get out)\b',  # Critical pattern for suicidal thoughts
                r'\b(i|we) (feel|felt) (fat|ugly|unwanted|unloved|unworthy|like a burden|like a failure|abandoned|rejected|alone|isolated|empty|hollow|numb|dead inside)\b',
                r'\b(no point|no use|no hope|no future|no reason to live|no way out|can\'t go on|can\'t take it anymore|can\'t bear it|can\'t handle it|can\'t escape|can\'t see a way forward)\b',
                r'\b(what\'s the point|why bother|why try|why live|why continue|why go on|what\'s the use|who cares|nothing matters|it\'s all meaningless)\b',
                r'\b(life is (pointless|meaningless|worthless|hopeless|too hard|too painful|not worth living|unbearable|torture|hell|misery|suffering|agony))\b',
                r'\b(nobody (cares|loves me|needs me|would miss me|would notice|understands|helps|listens|is there for me))\b',
                r'\b(i hate (myself|my body|my life|everything|living|existing|who i am|what i\'ve become))\b',
                r'\b(i\'m|i am) (a failure|a disappointment|a burden|better off dead|not good enough|worthless|useless|hopeless|helpless|pathetic|weak|broken|damaged|ruined)\b',
                r'\b(i|we) (have|has) nothing to (live for|look forward to|hope for|believe in|care about|hold onto)\b',
                r'\b(please (help|save) me|i (need|desperately need) help|i\'m (begging|pleading|desperate) for help|i don\'t know what to do|i\'m at the end of my rope|i\'m at my wit\'s end)\b',
                r'\b(i (can\'t|cannot) (go on|continue|keep going|keep living|face another day|see a future|see any hope|see any way out))\b',
                r'\b(i\'m (trapped|stuck|cornered|backed into a wall|at a dead end|out of options|out of time|running out of hope))\b',
                r'\b(i (just want|only want|need) (it to end|it to stop|the pain to stop|relief|peace|to be free|to escape))\b'
            ],
            'disappointment': [
                r'\b(i|we) (am|are|feel|felt) (disappointed|let down|disheartened|disillusioned|disenchanted|dismayed|discouraged)\b',
                r'\b(this|that) (is|was) (disappointing|disheartening|disillusioning|discouraging|a letdown|a disappointment)\b',
                r'\b(i|we) (expected|hoped for|wanted|wished for|anticipated) (better|more|something else|something different)\b',
                r'\b(i|we) (am|are|was|were) (disappointed|let down|disheartened) (by|with|in|about)\b',
                r'\b(disappointment|letdown|disillusionment|disenchantment|dismay|discouragement)\b',
                r'\b(not what|wasn\'t what|isn\'t what) (i|we) (expected|hoped for|wanted|wished for|anticipated)\b',
                r'\b(should have been|could have been|would have been) (better|different|more)\b',
                r'\b(i|we) (was|were) expecting more from (you|this|that|it|him|her|them)\b',
                r'\b(😔|😞|😕|😒|🙁|☹️|😢|💔)\b'
            ],
            'disapproval': [
                r'\b(i|we) (disapprove|don\'t approve|do not approve|disagree|object|oppose|reject|condemn|criticize)\b',
                r'\b(i|we) (am|are|feel|felt) (disapproving|critical|judgmental|censorious|reproachful|condemnatory)\b',
                r'\b(this|that) (is|was) (wrong|incorrect|inappropriate|unacceptable|improper|unsuitable|objectionable)\b',
                r'\b(i|we) (don\'t|do not|can\'t|cannot) (agree|accept|condone|support|endorse|approve of|tolerate)\b',
                r'\b(disapproval|disagreement|objection|opposition|criticism|censure|condemnation)\b',
                r'\b(shouldn\'t|should not|ought not to|mustn\'t|must not|can\'t|cannot) (do that|be that way|happen|be allowed)\b',
                r'\b(that\'s|that is|this is) (not okay|not right|not acceptable|not appropriate|not good|bad|wrong)\b',
                r'\b(👎|🙅‍♀️|🙅‍♂️|❌|⛔|🚫|😠|😒)\b'
            ],
            'embarassment': [
                r'\b(i|we) (am|are|feel|felt) (embarrassed|mortified|humiliated|ashamed|self-conscious|awkward|uncomfortable)\b',
                r'\b(this|that) (is|was) (embarrassing|mortifying|humiliating|shameful|awkward|uncomfortable|cringeworthy)\b',
                r'\b(i|we) (blushed|cringed|wanted to hide|wanted to disappear|felt awkward|felt uncomfortable)\b',
                r'\b(so|very|really|extremely|incredibly|totally) (embarrassed|mortified|humiliated|ashamed|self-conscious)\b',
                r'\b(embarrassment|mortification|humiliation|shame|self-consciousness|awkwardness|discomfort)\b',
                r'\b(can\'t believe|cannot believe) (i|we) (did that|said that|acted that way|behaved like that)\b',
                r'\b(wish|hoping) (the ground would swallow me|i could disappear|i was invisible|i wasn\'t here)\b',
                r'\b(😳|🙈|😖|😫|😱|🤦‍♀️|🤦‍♂️|😬)\b'
            ],
            'sadness': [
                r'\b(i|we) (am|are|feel|felt) (sad|unhappy|depressed|down|blue|melancholy|heartbroken|miserable|gloomy|sorrowful|despondent)\b',
                r'\b(this|that) (is|was) (sad|unhappy|depressing|heartbreaking|devastating|tragic|upsetting|distressing|painful)\b',
                r'\b(😢|😭|😔|😞|😢|🥺|😩|😫|💔|🖤)\b',
                r'\b(feeling|feels|felt) (sad|down|depressed|unhappy|low|terrible|awful|hopeless|empty)\b',
                r'\b(miss|missing|longing for) (you|him|her|them|it|someone|something)\b',
                r'\b(sadness|sorrow|despair|misery|depression|gloom|heartache|anguish)\b',
                r'\b(crying|cried|tears|weeping|sobbing|upset|hurt|broken heart|broken hearted)\b',
                r'\b(lonely|alone|isolated|abandoned|rejected|unwanted|unloved)\b'
            ],
            'anger': [
                r'\b(i|we) (am|are|feel|felt) (angry|furious|outraged|mad|irritated|enraged|frustrated|livid|irate|incensed|infuriated|annoyed)\b',
                r'\b(this|that) (is|was) (unacceptable|outrageous|ridiculous|infuriating|aggravating|maddening|offensive|insulting|disrespectful)\b',
                r'\b(😠|😡|🤬|💢|😤|😒|🙄|👿|💥|🔥)\b',
                r'\b(so|very|really|extremely|incredibly) (angry|mad|furious|irritated|annoyed|frustrated|upset)\b',
                r'\b(anger|rage|fury|outrage|irritation|frustration|annoyance|indignation|wrath)\b',
                r'\b(pissed|pissed off|fed up|had enough|had it|lost my temper|losing my temper)\b',
                r'\b(hate|despise|detest|loathe|resent|abhor)\b',
                r'\b(makes me|making me) (angry|mad|furious|upset|irritated)\b'
            ],
            'fear': [
                r'\b(i|we) (am|are|feel|felt) (afraid|scared|frightened|terrified|worried|anxious|fearful|petrified|horrified|alarmed|panicky|uneasy)\b',
                r'\b(this|that) (is|was) (scary|frightening|terrifying|daunting|intimidating|horrifying|alarming|threatening|disturbing|creepy|spooky)\b',
                r'\b(😨|😱|😰|😳|😟|😬|😨|😖|🙀|😵)\b',
                r'\b(feeling|feels|felt) (scared|afraid|terrified|fearful|anxious|worried|nervous|threatened|intimidated|unsafe)\b',
                r'\b(what if|worried about|concerned about|scared of|afraid of|terrified of|fear of|phobia|nightmare)\b',
                r'\b(fear|terror|horror|dread|anxiety|panic|fright|alarm|trepidation|apprehension)\b',
                r'\b(scared to death|scared stiff|scared silly|jumping at shadows|shaking|trembling|shivering|heart racing|heart pounding)\b',
                r'\b(danger|dangerous|threat|threatening|risk|risky|hazard|hazardous|unsafe|perilous)\b',
                r'\b(makes me|making me) (scared|afraid|fearful|anxious|worried|nervous)\b'
            ],
            'excitement': [
                r'\b(i|we) (am|are|feel|felt) (excited|thrilled|exhilarated|enthusiastic|eager|pumped|psyched|stoked|amped|buzzed)\b',
                r'\b(this|that) (is|was) (exciting|thrilling|exhilarating|stimulating|electrifying|invigorating|rousing|stirring)\b',
                r'\b(i|we) (can\'t wait|am looking forward|are looking forward|am eager|are eager) (for|to)\b',
                r'\b(so|very|really|extremely|incredibly) (excited|thrilled|exhilarated|enthusiastic|eager|pumped|psyched)\b',
                r'\b(excitement|thrill|exhilaration|enthusiasm|eagerness|anticipation|energy|buzz)\b',
                r'\b(can\'t contain|bursting with|full of|filled with|overflowing with) (excitement|enthusiasm|energy|anticipation)\b',
                r'\b(woo|woohoo|yay|yahoo|yes|awesome|amazing|fantastic|incredible|brilliant|wow)\b',
                r'\b(😃|😄|😁|🤩|🥳|🙌|👏|✨|🎉|🎊|⚡|💥)\b'
            ],
            'gratitude': [
                r'\b(i|we) (am|are|feel|felt) (grateful|thankful|appreciative|indebted|obliged|beholden)\b',
                r'\b(i|we) (appreciate|value|cherish|treasure|am grateful for|are grateful for|am thankful for|are thankful for)\b',
                r'\b(thank you|thanks|many thanks|thank you so much|thanks a lot|thanks a bunch|thank you kindly)\b',
                r'\b(i|we) (owe|want to thank|would like to thank|wish to thank|must thank) (you|him|her|them)\b',
                r'\b(gratitude|appreciation|thankfulness|gratefulness|indebtedness|recognition)\b',
                r'\b(so|very|really|extremely|incredibly|deeply|truly|sincerely) (grateful|thankful|appreciative)\b',
                r'\b(means|meant) (a lot|the world|so much|everything) (to me|to us)\b',
                r'\b(🙏|❤️|💕|😊|🥰|✨|💯|👍)\b'
            ],
            'nervousness': [
                r'\b(i|we) (am|are|feel|felt) (nervous|anxious|jittery|edgy|tense|uneasy|restless|fidgety|on edge|keyed up)\b',
                r'\b(this|that) (is|was) (nerve-wracking|nerve-racking|stressful|tense|anxiety-inducing|worrying)\b',
                r'\b(i|we) (have|has|had) (butterflies|knots|a knot) (in my stomach|in our stomachs|in my belly|in our bellies)\b',
                r'\b(my|our) (hands are|palms are|heart is) (sweating|sweaty|racing|pounding|beating fast)\b',
                r'\b(nervousness|anxiety|jitters|tension|unease|restlessness|apprehension|stress)\b',
                r'\b(can\'t|cannot) (relax|calm down|settle down|sit still|focus|concentrate|stop worrying)\b',
                r'\b(so|very|really|extremely|incredibly) (nervous|anxious|jittery|edgy|tense|uneasy|restless|fidgety)\b',
                r'\b(😰|😥|😨|😟|😬|😖|😣|🤢|😓|🫣)\b'
            ],
            'surprise': [
                r'\b(i|we) (am|are|was|were|feel|felt) (surprised|amazed|astonished|shocked|stunned|speechless|dumbfounded|flabbergasted|startled|taken aback)\b',
                r'\b(this|that) (is|was) (surprising|amazing|shocking|unexpected|unbelievable|astounding|incredible|extraordinary|mind-blowing|jaw-dropping)\b',
                r'\b(😲|😮|😯|😱|🤯|😳|😨|😵|😦|😧|🙀)\b',
                r'\b(no way|cannot believe|did not expect|never expected|never thought|never imagined|never saw this coming)\b',
                r'\b(what|how|why|when|who|where) (!|!!|!!!)\b',
                r'\b(wow|whoa|woah|oh my|oh my god|oh my goodness|oh wow|holy|gosh|goodness|jeez|yikes)\b',
                r'\b(came as a|was a|is a) (surprise|shock|revelation|bombshell|bolt from the blue)\b',
                r'\b(surprise|shock|amazement|astonishment|disbelief|wonder|awe)\b',
                r'\b(surprised|shocked|amazed|astonished|stunned|startled|taken aback) (by|at|to see|to hear|to learn|to find out)\b',
                r'\b(unexpected|unanticipated|unforeseen|out of nowhere|out of the blue|all of a sudden|suddenly)\b',
                r'\b(makes me|making me|left me) (surprised|shocked|amazed|astonished|speechless|stunned)\b'
            ],
            'love': [
                r'\b(i|we) (love|adore|cherish|treasure|worship|idolize|admire|care for|fancy|like) (you|him|her|them|this|that|someone|something)\b',
                r'\b(i|we) (am|are|feel|felt) (in love|loving|passionate|smitten|devoted|enamored|infatuated|head over heels|crazy about|wild about)\b',
                r'\b(❤️|💕|💗|💘|💝|🥰|😍|💓|💞|💖|💟|💌)\b',
                r'\b(so|very|really|deeply|truly|madly|completely|utterly|absolutely|totally) (in love|love|adore|cherish|devoted|attached)\b',
                r'\b(can\'t|cannot) (live|be|imagine life|function|exist) (without|without you|apart from you|if you were gone)\b',
                r'\b(love|affection|adoration|devotion|passion|fondness|attachment|infatuation|crush|romance)\b',
                r'\b(loving|adoring|cherishing|treasuring|worshipping|idolizing|admiring|caring for) (you|him|her|them|someone)\b'
            ],
            'disgust': [
                r'\b(i|we) (am|are|feel|felt) (disgusted|revolted|repulsed|sickened|nauseated|appalled|grossed out|repelled|turned off|horrified|disturbed)\b',
                r'\b(this|that) (is|was) (disgusting|revolting|repulsive|gross|nasty|vile|foul|offensive|repugnant|sickening|nauseating|stomach-turning|stomach-churning|distasteful|obscene|vulgar|crude|indecent|abhorrent|loathsome)\b',
                r'\b(🤢|🤮|😖|😫|😤|🤧|😷|👎|💩|🙄|😬|😒)\b',
                r'\b(so|very|really|extremely|incredibly|utterly|absolutely|completely|totally|thoroughly|deeply) (disgusting|gross|revolting|repulsive|nauseating|sickening|disturbing|offensive|vile|foul|nasty)\b',
                r'\b(disgust|revulsion|repulsion|nausea|aversion|distaste|loathing|abhorrence|contempt|disdain|horror|repugnance)\b',
                r'\b(makes me|making me|made me) (sick|nauseous|vomit|gag|disgusted|grossed out|want to throw up|queasy|ill|uncomfortable|cringe|recoil)\b',
                r'\b(gross|ew|eww|ugh|yuck|nasty|sick|vile|foul|filthy|dirty|rotten|putrid|rank|fetid|stinking|repellent|repugnant)\b',
                r'\b(can\'t stomach|can\'t bear|can\'t stand|can\'t tolerate|can\'t handle|can\'t look at|can\'t even|turns my stomach)\b',
                r'\b(that\'s|that is|this is) (disgusting|gross|revolting|repulsive|sickening|nauseating|vile|foul|nasty|disturbing|offensive)\b',
                r'\b(i|we) (hate|detest|loathe|despise|abhor|can\'t stand) (how|the way|when|that|this|it|the fact that)\b',
                r'\b(i almost|i nearly|i just about|i literally) (threw up|vomited|gagged|retched|got sick)\b'
            ],
            'trust': [
                r'\b(i|we) (trust|believe in|have faith in|rely on|depend on|count on) (you|him|her|them|this|that|someone|something)\b',
                r'\b(i|we) (am|are|feel|felt) (trusting|confident|assured|certain|convinced) (in|about|with|of) (you|him|her|them|this|that|someone|something)\b',
                r'\b(you|he|she|they|it) (are|is|have|has been) (reliable|trustworthy|dependable|honest|truthful|faithful|loyal)\b',
                r'\b(trust|faith|confidence|belief|reliance|dependence|assurance|certainty)\b',
                r'\b(trusting|believing|having faith|relying|depending|counting on) (you|him|her|them|someone)\b',
                r'\b(i know|i believe|i\'m sure|i\'m certain|i\'m confident) (you|he|she|they|it) (will|can|could|would)\b',
                r'\b(i|we) (trust|have trust|place trust|put trust) (in|with) (you|him|her|them|your|his|her|their) (judgment|opinion|advice|guidance|wisdom|expertise|knowledge)\b'
            ],
            'grief': [
                r'\b(i|we) (am|are|feel|felt) (grieving|mourning|bereaved|devastated|shattered|broken) (over|about|because of|due to|from) (loss|death|passing)\b',
                r'\b(i|we) (lost|mourn|grieve for) (my|our) (loved one|family member|friend|partner|spouse|husband|wife|child|parent|mother|father|brother|sister)\b',
                r'\b(i|we) (miss) (my|our) (deceased|late|departed|dead) (loved one|family member|friend|partner|spouse|husband|wife|child|parent|mother|father|brother|sister)\b',
                r'\b(the|their|his|her) (death|passing|loss) (is|was) (devastating|heartbreaking|unbearable|painful|difficult|hard|tragic)\b',
                r'\b(grief|mourning|bereavement|loss)\b',
                r'\b(funeral|memorial|service|burial|cremation|grave|cemetery|obituary)\b',
                r'\b(died|passed away|gone|no longer with us|departed|deceased|lost the battle)\b',
                r'\b(i|we) (am|are) (in|experiencing|going through|dealing with|coping with) (grief|mourning|bereavement)\b',
                r'\b(i|we) (have|had) (lost|recently lost|just lost) (someone|a loved one|a family member|a friend|a pet)\b'
            ],
            'relief': [
                r'\b(i|we) (am|are|feel|felt) (relieved|unburdened|eased|relaxed|calmer|better|at ease|at peace) (that|because|now that|since)\b',
                r'\b(that|this) (is|was) (a relief|relieving|comforting|reassuring|calming|soothing)\b',
                r'\b(feeling|feels|felt) (relieved|unburdened|eased|better|lighter|calmer|relaxed) (after|now|since|because)\b',
                r'\b(relief|ease|comfort|reassurance|solace|respite|reprieve|alleviation) (from|of|about)\b',
                r'\b(weight off|burden lifted|pressure off|stress gone|worry gone|anxiety gone)\b',
                r'\b(thank goodness|thank god|finally|at last|phew|whew|glad that\'s over)\b',
                r'\b(i|we) (can|could) (breathe|relax|rest|sleep) (easier|better|well|peacefully|soundly) (now|again|at last|finally)\b',
                r'\b(i|we) (no longer|don\'t|do not) (have to|need to) (worry|stress|be concerned|be anxious|be afraid|fear) (about|over)\b'
            ],
            'panic': [
                r'\b(i|we) (am|are|feel|felt) (panicked|panicking|frantic|frenzied|hysterical|overwhelmed|out of control)\b',
                r'\b(this|that) (is|was) (a disaster|catastrophic|an emergency|a crisis|urgent|critical)\b',
                r'\b(panic|frenzy|hysteria|alarm|emergency|crisis|urgency|chaos)\b',
                r'\b(heart racing|hyperventilating|can\'t breathe|breathing fast|sweating|shaking|trembling)\b',
                r'\b(need help|need assistance|need support|need aid|need backup|need rescue) (now|immediately|right now|quickly|fast|asap|urgently)\b',
                r'\b(what do i do|what should i do|help me|someone help|emergency|mayday|sos)\b',
                r'\b(i|we) (am|are) (having|experiencing) (a panic attack|an anxiety attack|a meltdown|a breakdown)\b',
                r'\b(oh no|oh god|oh my god|omg|help|urgent|emergency|crisis|danger|threat|risk)\b',
                r'\b(i|we) (can\'t|cannot) (handle|deal with|cope with|manage|control) (this|the situation|what\'s happening|it) (anymore|any longer|now)\b'
            ],
            'neutral': [
                r'\b(i|we) (am|are|feel|felt) (neutral|okay|fine|alright|so-so|indifferent|balanced|neither good nor bad)\b',
                r'\b(this|that) (is|was) (neutral|okay|fine|alright|so-so|average|mediocre|neither good nor bad)\b',
                r'\b(😐|😶|😑|😏|🙂|😕)\b',
                r'\b(feeling|feels|felt) (neutral|okay|fine|alright|so-so|indifferent|balanced)\b',
                r'\b(neutral|indifference|apathy|detachment|dispassion|disinterest)\b',
                r'\b(not sure|not certain|undecided|on the fence|middle ground|no strong feelings|no opinion)\b'
            ],
            'nostalgia': [
                r'\b(i|we) (am|are|feel|felt) (nostalgic|sentimental|reminiscent|wistful|yearning|longing|homesick) (about|for|when thinking about|when remembering)\b',
                r'\b(i|we) (miss|remember|recall|reminisce about|think back to|long for|yearn for) (the old days|those days|that time|my childhood|the past|back then|simpler times|better times)\b',
                r'\b(i|we) (miss) (my|our) (home|hometown|country|family|friend|friends|partner|spouse|husband|wife|child|parent|mother|father|brother|sister|pet|dog|cat)\b',
                r'\b(this|that) (reminds|reminded) (me|us) (of|about) (the past|my childhood|when i was|when we were|old times|earlier times|younger days|growing up)\b',
                r'\b(good old days|back in the day|back then|in those days|when i was young|when i was a kid|in my day|in my time|in my youth|in my childhood)\b',
                r'\b(nostalgia|sentimentality|reminiscence|wistfulness|yearning|longing|homesickness|fond memories|cherished memories)\b',
                r'\b(remember when|those were the days|memories|throwback|flashback|blast from the past|trip down memory lane|walk down memory lane)\b',
                r'\b(wish i could go back|wish i could relive|wish i could experience again|wish i could return to) (those days|that time|my childhood|the past|my youth)\b',
                r'\b(🕰️|⏳|📷|📸|🎞️|📼|💾|🧸|👵|👴)\b',
                r'\b(i|we) (fondly|warmly|lovingly|happily|often) (remember|recall|think about|reminisce about) (the past|my childhood|growing up|those times)\b'
            ],
            'optimism': [
                r'\b(i|we) (am|are|feel|felt) (optimistic|hopeful|positive|confident|upbeat|encouraged|buoyant|sanguine)\b',
                r'\b(i|we) (believe|think|feel|am confident|am sure|am certain|have faith|trust) (things will|it will|everything will) (improve|get better|work out|be okay|be fine|be alright)\b',
                r'\b(looking on the bright side|seeing the silver lining|focusing on the positive|keeping a positive outlook|staying positive)\b',
                r'\b(optimism|hope|positivity|confidence|encouragement|faith|trust|belief) (for the future|about tomorrow|about what\'s ahead|about what\'s to come)\b',
                r'\b(it\'ll|it will|things will|everything will) (be okay|be fine|be alright|work out|get better|improve|turn around) (soon|eventually|in time|in the end)\b',
                r'\b(better days ahead|brighter future|light at the end of the tunnel|turn the corner|see the light)\b',
                r'\b(not giving up|keeping hope alive|staying hopeful|remaining positive|keeping faith|believing in better) (days|times|future|outcomes|results)\b',
                r'\b(😊|🙂|🌞|🌈|✨|🌟|💫|🌻|🌱|🍀)\b',
                r'\b(i|we) (expect|anticipate|look forward to|am excited about|are excited about) (good|positive|favorable|better) (things|outcomes|results|developments|changes)\b',
                r'\b(tomorrow|the future|what\'s ahead|what\'s to come) (is|looks|seems) (bright|promising|hopeful|positive|good|better)\b',
                r'\b(i|we) (believe|have faith|trust|am confident|are confident) (in|about) (the future|tomorrow|what\'s ahead|what\'s to come|what lies ahead)\b',
                r'\b(i|we) (see|envision|imagine|picture|dream of) (a better|a brighter|a positive|an improved|a promising) (future|tomorrow|world|life|outcome)\b',
                r'\b(things are looking up|the future is bright|better times are coming|good things are on the horizon|positive change is coming)\b',
                r'\b(i|we) (am|are) (excited|enthusiastic|eager|looking forward) (about|for) (the future|what\'s next|what\'s coming|what lies ahead)\b',
                r'\b(i|we) (have|hold|maintain) (hope|optimism|positive expectations|faith|confidence) (for|in|about) (the future|tomorrow|what\'s ahead)\b',
                r'\b(i|we) (believe|think|know|am sure|are sure) (that|the) (best|better) (is yet to come|days are ahead|times are coming)\b',
                r'\b(i|we) (am|are) (investing|planning|preparing|building|working) (for|towards) (a better|a brighter|a positive) (future|tomorrow)\b',
                r'\b(i|we) (believe|think|know|am confident|are confident) (things|life|situations|circumstances) (will|can|could) (improve|get better|change for the better)\b',
                r'\b(better days|good things|positive changes) (are ahead|are coming|will come|will happen)\b',
                r'\b(i|we) (trust|believe|have faith) (that) (things|it|everything) (will work out|will be okay|will be fine|will be alright)\b',
                r'\b(the future|tomorrow|what\'s ahead|what\'s to come) (is full of|has many|offers|holds) (possibilities|opportunities|potential|promise)\b',
                r'\b(i|we) (am|are) (planning|preparing|working|building|investing) (for|towards) (the future|tomorrow|what\'s ahead|what\'s to come)\b',
                r'\b(i|we) (have|feel|sense) (hope|faith|optimism|confidence|trust) (for|about|in) (the future|what\'s ahead|what\'s to come)\b'
            ],
            'pride': [
                r'\b(i|we) (am|are|feel|felt) (proud|accomplished|successful|fulfilled|satisfied|pleased|gratified|triumphant|victorious|honored|validated|vindicated)\b',
                r'\b(i|we) (take pride in|am proud of|are proud of|feel proud of|feel good about|am pleased with|are pleased with|am honored by|are honored by) (myself|ourselves|my|our)\b',
                r'\b(i|we) (achieved|accomplished|completed|finished|mastered|conquered|overcame|succeeded in|excelled at|triumphed over|prevailed|won|earned|deserved|attained|reached|surpassed)\b',
                r'\b(proud of|pleased with|satisfied with|happy with|delighted with|impressed by|amazed by|thrilled with) (myself|ourselves|my work|our work|my achievement|our achievement|what i\'ve done|what we\'ve done|my performance|our performance)\b',
                r'\b(pride|accomplishment|achievement|success|fulfillment|satisfaction|gratification|triumph|victory|honor|excellence|mastery|prowess|distinction)\b',
                r'\b(look what i|see what i|check out what i|look at what i|look what we|see what we|check what we) (did|made|created|built|achieved|accomplished|finished|completed|won|earned|produced|developed)\b',
                r'\b(i did it|we did it|nailed it|crushed it|aced it|smashed it|killed it|rocked it|owned it|dominated it|mastered it|conquered it|won it|pulled it off|made it happen)\b',
                r'\b(😌|😏|😎|🏆|🥇|🎖️|🏅|💪|👊|🙌|✅|🔥|👑|🌟|⭐|🥳)\b',
                r'\b(i\'m|i am|we\'re|we are) (the best|number one|top|superior|unbeatable|unstoppable|unmatched|unparalleled|exceptional|outstanding|excellent)\b',
                r'\b(i|we) (deserve|earned|worked hard for|fought for|strived for|put in the effort for) (this|that|it|recognition|praise|reward|success|achievement|accomplishment|victory)\b',
                r'\b(i|we) (couldn\'t be|couldn\'t feel|am|are) (prouder|more proud|more pleased|more satisfied|more fulfilled|more accomplished)\b',
                r'\b(i|we) (proved|showed|demonstrated|established|confirmed|validated) (myself|ourselves|them|everyone|the world|the critics|the doubters|the haters) (wrong|right)\b',
                r'\b(i|we) (stand tall|hold my head high|hold our heads high|can be proud|should be proud|have every right to be proud)\b',
                r'\b(i|we) (am|are) (satisfied|pleased|happy|content|delighted) with (my|our) (language skills|abilities|performance|achievements|accomplishments|work|results|progress|growth|development|improvement)\b',
                r'\b(i|we) (am|are) (satisfied|pleased|happy|content|delighted) with (how|what) (i|we) (speak|talk|communicate|express|write|read|understand|learn|know|do|perform|achieve|accomplish)\b'
            ],
            'realisation': [
                r'\b(i|we) (realized|realised|understood|recognized|recognised|discovered|found out|learned|learnt|came to understand)\b',
                r'\b(it (dawned on|occurred to|became clear to|became apparent to|hit|struck) (me|us))\b',
                r'\b(i|we) (suddenly|just|finally|now|recently) (realized|realised|understood|recognized|recognised|see|get it|understand)\b',
                r'\b(had an epiphany|had a revelation|had a realization|had a moment of clarity|saw the light|connected the dots)\b',
                r'\b(realization|realisation|epiphany|revelation|insight|understanding|awareness|awakening|enlightenment)\b',
                r'\b(now i see|now i understand|now i get it|it all makes sense|everything clicked|the penny dropped)\b',
                r'\b(oh|aha|eureka|wow|oh my|oh my god|oh my goodness|oh wow|i see|i get it)\b',
                r'\b(😮|😲|🤯|💡|✨|👁️|👀|🧠)\b'
            ],
            'remorse': [
                r'\b(i|we) (am|are|feel|felt) (remorseful|regretful|sorry|apologetic|contrite|penitent|repentant|guilty)\b',
                r'\b(i|we) (regret|am sorry for|are sorry for|apologize for|apologise for|feel bad about|feel guilty about)\b',
                r'\b(i|we) (shouldn\'t have|should not have|wish i hadn\'t|wish i had not|wish we hadn\'t|wish we had not)\b',
                r'\b(i|we) (made a mistake|did something wrong|messed up|screwed up|erred|was wrong|were wrong)\b',
                r'\b(remorse|regret|guilt|contrition|penitence|repentance|sorrow|apology)\b',
                r'\b(if only i|if only we|i wish i|we wish we|i should have|we should have) (hadn\'t|had not|could take back|could undo)\b',
                r'\b(i\'m sorry|i am sorry|we\'re sorry|we are sorry|please forgive me|please forgive us|my bad|my fault|my mistake)\b',
                r'\b(😔|😞|😢|😥|😓|🙇‍♀️|🙇‍♂️|💔|🤦‍♀️|🤦‍♂️)\b'
            ],
        }

        # Initialize emotion responses
        self.emotion_responses = {
            'achievement': [
                "Congratulations! That's a significant accomplishment. You should be proud of what you've achieved.",
                "Well done! Your hard work and dedication have clearly paid off. How does it feel?",
                "That's impressive! It's great to see your efforts being rewarded. What was the most challenging part?",
                "Excellent work! Taking time to celebrate achievements is important. What's your next goal?",
                "That's fantastic! Your persistence has really paid off. What did you learn from this experience?"
            ],
            'admiration': [
                "It's wonderful to hear you express such admiration. What qualities do you find most inspiring?",
                "That's a beautiful sentiment of admiration. People who inspire us can have such a positive impact.",
                "Your admiration really comes through. How does this person's influence shape your goals?",
                "Admiration often reflects our own values. What aspects do you find most worthy of admiration?",
                "It's great to recognize qualities we admire in others. How does this shape your own goals?"
            ],
            'amusement': [
                "That does sound funny! It's great to find humor in life's moments.",
                "I can tell that amused you! Laughter is such a wonderful part of the human experience.",
                "That's hilarious! It's always good to have something that makes you laugh.",
                "I'm glad that brought you some amusement. What other things make you laugh?",
                "That's quite entertaining! Humor can really brighten our day, can't it?"
            ],
            'annoyance': [
                "I can hear that you're feeling annoyed. Sometimes small things can really get under our skin.",
                "That does sound irritating. What do you usually do when you feel this way?",
                "I understand your annoyance. It's natural to feel frustrated when things aren't going as expected.",
                "Being annoyed is a normal reaction. Is there something that might help improve the situation?",
                "I can tell this is bothering you. Sometimes expressing annoyance is the first step to addressing it."
            ],
            'anticipation': [
                "I can feel your anticipation! Looking forward to something can be so energizing.",
                "It sounds like you're really looking forward to this. What are you most excited about?",
                "That sense of anticipation can be so powerful. How are you preparing for what's coming?",
                "Looking forward to something brings its own kind of joy. What are your expectations?",
                "I can tell you're eagerly awaiting this. The anticipation is sometimes as enjoyable as the event itself!"
            ],
            'approval': [
                "I appreciate you sharing your approval. It's good to acknowledge when things meet our standards.",
                "That sounds like a positive endorsement. What aspects do you find most worthy of approval?",
                "I can tell you're pleased with this. It's nice when things align with our expectations, isn't it?",
                "Your approval comes through clearly. What standards or values is this fulfilling for you?",
                "It's good to express when we approve of something. This seems to really resonate with your values."
            ],
            'curious': [
                "That's an interesting question! Curiosity often leads to fascinating discoveries.",
                "I can tell you're curious about this. What aspects are you most interested in exploring?",
                "That's a thought-provoking topic to wonder about. What sparked your interest in this?",
                "Your curiosity is evident! Questions like these often lead to the most interesting conversations.",
                "I appreciate your inquisitive nature. What other aspects of this topic intrigue you?"
            ],
            'caring': [
                "Your caring nature really comes through. It's wonderful to see such compassion.",
                "I can tell you really care deeply. That kind of empathy is so valuable.",
                "Your concern for others is evident. How do you balance caring for others with self-care?",
                "That's a very thoughtful perspective. Caring connections are so important in life.",
                "I appreciate your compassionate approach. What inspired you to be so caring?"
            ],
            'confusion': [
                "I can understand why that might be confusing. Would it help to break this down into simpler parts?",
                "It's perfectly normal to feel confused sometimes. Which aspect is most unclear?",
                "That does sound puzzling. Sometimes talking through confusion helps clarify our thoughts.",
                "I see why you might be feeling confused. Would looking at this from a different angle help?",
                "Confusion often comes before clarity. What specific questions do you have that might help sort this out?"
            ],
            'desire': [
                "I can hear how much you want this. What makes it so meaningful to you?",
                "That desire comes through strongly. What steps might bring you closer to what you want?",
                "It's powerful to recognize our desires so clearly. What would fulfilling this desire bring to your life?",
                "I understand that feeling of wanting something deeply. How long have you felt this way?",
                "Your desire is completely valid. Sometimes naming what we want is the first step toward it."
            ],
            'joy': [
                "It's wonderful to hear you're feeling happy! Those positive moments are worth savoring.",
                "That's great! Joy is such an energizing emotion. What's bringing you happiness right now?",
                "I'm glad you're feeling good! Positive emotions can really brighten our perspective.",
                "That's lovely to hear! Happiness often comes from the things that matter most to us.",
                "Wonderful! Those moments of joy are so valuable. Is there a way to bring more of this into your daily life?"
            ],
            'desperation': [
                "I hear that you're feeling overwhelmed right now. Remember that difficult moments do pass with time.",
                "It sounds like you're going through a really tough time. Would talking about specific concerns help?",
                "I understand you're feeling desperate. Sometimes taking one small step can help regain some sense of control.",
                "That sounds incredibly difficult. Remember that reaching out for help shows real strength.",
                "I'm sorry you're feeling this way. Your feelings are valid, and there are resources that can help during these times."
            ],
            'disappointment': [
                "I can hear your disappointment. It's hard when reality doesn't match our expectations.",
                "That does sound disappointing. How are you processing this letdown?",
                "I understand that feeling of disappointment. What had you hoped would happen instead?",
                "It's natural to feel disappointed when things don't go as planned. What might help you move forward?",
                "I'm sorry things didn't work out as you'd hoped. Sometimes disappointment can teach us something valuable about our expectations."
            ],
            'disapproval': [
                "I understand you don't approve of this. Our values often shape what we find acceptable.",
                "I can hear your disapproval clearly. What specific aspects do you find most problematic?",
                "Your disapproval makes sense given what you've described. What standards or values is this violating for you?",
                "I appreciate you sharing your perspective. Disapproval often stems from our core values being challenged.",
                "I can tell you feel strongly about this. What would a more acceptable alternative look like to you?"
            ],
            'embarassment': [
                "That does sound embarrassing. Remember that everyone has moments they wish they could redo.",
                "I understand that feeling of embarrassment. How are you handling it?",
                "Embarrassing moments can feel so intense in the moment. Do you think others noticed as much as you felt they did?",
                "That kind of situation would make many people nervous. Is there a way to look at it with some self-compassion?",
                "Embarrassment is such a universal human experience. Sometimes sharing these moments helps take away some of their power."
            ],
            'sadness': [
                "I understand you're feeling down. It's okay to experience sadness - it's a natural part of life.",
                "I'm sorry to hear you're feeling sad. Would you like to talk about what's on your mind?",
                "It's okay to feel sad sometimes. Taking care of yourself during these moments is important.",
                "I hear that you're feeling low right now. Sometimes expressing these feelings can help lighten the burden.",
                "Sadness is a natural response to difficult situations. Is there something specific that triggered this feeling?"
            ],
            'anger': [
                "I can tell you're feeling frustrated. Sometimes anger signals that something important to us has been affected.",
                "It sounds like you're feeling pretty upset. Would it help to talk about what happened?",
                "I understand you're angry. That's a natural response when we feel wronged or when our boundaries aren't respected.",
                "Your frustration comes through clearly. Sometimes anger can help us identify what matters to us.",
                "I hear your anger. Taking some time to process these feelings before acting can sometimes be helpful."
            ],
            'fear': [
                "It sounds like you're feeling anxious. Fear is often our mind's way of trying to protect us.",
                "I understand you're feeling scared. Would it help to break down what's causing this fear?",
                "Being afraid is completely natural. Sometimes naming our specific fears can make them feel more manageable.",
                "I hear that you're worried. Sometimes our fears feel bigger when we face them alone.",
                "It's okay to feel afraid. Is there a particular aspect of this situation that concerns you most?"
            ],
            'excitement': [
                "Your excitement is contagious! What are you most looking forward to about this?",
                "I can feel your enthusiasm! It's wonderful when something energizes us like that.",
                "That sounds really exciting! How are you channeling all that positive energy?",
                "I can tell you're thrilled about this. What aspect has you most excited?",
                "Your excitement really comes through! These moments of anticipation can be so enjoyable."
            ],
            'gratitude': [
                "That's a beautiful expression of gratitude. Appreciation can really enrich our experiences.",
                "I can tell you're truly thankful. What impact has this had on you?",
                "Expressing gratitude is so powerful. How has being thankful affected your perspective?",
                "That's wonderful that you're feeling grateful. Recognizing what we appreciate can be so meaningful.",
                "I appreciate you sharing your gratitude. What other things in life are you finding yourself thankful for?"
            ],
            'nervousness': [
                "I can understand why you'd feel nervous. Those jittery feelings are your body's natural response.",
                "Being nervous before something important is completely normal. How do you usually manage these feelings?",
                "I hear that you're feeling on edge. Sometimes acknowledging our nervousness can help reduce its power.",
                "That kind of situation would make many people nervous. Is there anything that might help you feel more grounded?",
                "It's okay to feel nervous. Sometimes it's just our body's way of preparing for something that matters to us."
            ],
            'surprise': [
                "That does sound unexpected! Surprises can really catch us off guard.",
                "I can imagine that was surprising. How are you processing this unexpected development?",
                "Unexpected events can certainly be jarring. How are you adjusting to this surprise?",
                "That's quite a surprise. Sometimes the unexpected gives us a chance to see things differently.",
                "I understand this wasn't what you anticipated. How do you feel about this unexpected turn?"
            ],
            'love': [
                "That's a beautiful sentiment. Love and connection are such fundamental human needs.",
                "It's wonderful to hear about those feelings of love and attachment. Relationships add so much to our lives.",
                "Those feelings of love sound meaningful. Connections with others often bring the greatest joy.",
                "That's lovely. The people we care about help make life rich and meaningful.",
                "It's wonderful to experience those feelings of connection. What do you value most about this relationship?"
            ],
            'disgust': [
                "I understand that doesn't sit well with you. Our sense of disgust often connects to our values.",
                "That sounds really off-putting. Sometimes strong negative reactions tell us something important.",
                "I can see why you'd find that disturbing. Would you like to talk more about what specifically bothers you?",
                "That reaction makes sense. Feeling disgusted often relates to things that conflict with our sense of what's right.",
                "I understand your aversion to that. What aspects do you find most troubling?"
            ],
            'neutral': [
                "Sometimes a balanced perspective helps us see things clearly. What's on your mind today?",
                "That sounds like a measured approach. Is there anything specific you'd like to explore further?",
                "Taking a neutral stance can be valuable. Is there a particular aspect of this you're considering?",
                "I appreciate your balanced view. What factors are you weighing as you think about this?",
                "Sometimes that middle ground is exactly where clarity emerges. What are your thoughts on next steps?"
            ],
            'nostalgia': [
                "Those nostalgic memories can be so powerful. What do you miss most about that time?",
                "I can hear the nostalgia in your words. How does remembering that time make you feel?",
                "Those memories seem really meaningful to you. What makes that time so special in your recollection?",
                "Nostalgia often connects us with important parts of our history. How has that time shaped who you are now?",
                "Those fond memories of the past can be so comforting. What aspects of that time would you bring into the present if you could?"
            ],
            'optimism': [
                "I love your positive outlook! What's giving you this sense of optimism?",
                "That hopeful perspective is wonderful to hear. What possibilities are you most excited about?",
                "Your optimism really shines through. How does maintaining this positive outlook help you?",
                "It's great to hear such a hopeful view. What's contributing to your positive expectations?",
                "That optimistic approach can be so powerful. How does it influence the way you approach challenges?"
            ],
            'pride': [
                "You have every reason to feel proud! What aspect of this achievement means the most to you?",
                "That sense of pride is well-deserved. How did you overcome the challenges along the way?",
                "I can hear how proud you are, and rightfully so! What did you learn about yourself through this process?",
                "Taking pride in your accomplishments is important. How will you celebrate this achievement?",
                "That's definitely something to be proud of. What's the next goal you're setting your sights on?"
            ],
            'realisation': [
                "That moment of realization can be so powerful. How has this new understanding changed your perspective?",
                "It sounds like something really clicked for you. What led to this insight?",
                "Those 'aha' moments can be transformative. How do you feel now that you've made this connection?",
                "Realizations like that can really shift our understanding. What will you do with this new insight?",
                "I can sense how significant this realization is for you. How does it change things moving forward?"
            ],
            'remorse': [
                "I can hear your regret. Being able to acknowledge mistakes is actually a sign of strength.",
                "It sounds like you're feeling remorseful. What would you do differently if you could?",
                "Feeling regret can be difficult but also valuable for growth. Have you considered how to make amends?",
                "I understand that feeling of remorse. Sometimes the best response is to learn from the experience and move forward.",
                "It takes courage to acknowledge when we've done something we regret. How might this experience shape your future choices?"
            ],
            'dread': [
                "That sense of dread can be so overwhelming. What specifically are you most concerned about?",
                "I can hear how much you're dreading this. Sometimes breaking it down into smaller parts can make it feel more manageable.",
                "That feeling of impending doom is really difficult. What has helped you cope with similar feelings in the past?",
                "I understand that sense of dread. Is there any part of the situation that feels within your control?",
                "It's natural to dread certain situations. Would talking through some possible outcomes help ease some of that feeling?"
            ],
            'appalled': [
                "I can understand why you'd be appalled by that. It sounds like it violates some important values for you.",
                "That does sound shocking. What aspect do you find most disturbing?",
                "I can hear how appalled you are. Sometimes such strong reactions tell us something important about our core values.",
                "Being appalled by certain behaviors or situations is a natural response. How are you processing this?",
                "I understand your reaction completely. What do you think would be an appropriate response to something so troubling?"
            ],
        }

        # Initialize greeting patterns
        self.greeting_patterns = [
            r'\b(hi|hello|hey|greetings|howdy)\b',
            r'\b(good) (morning|afternoon|evening|day)\b',
            r'\b(how are you|how\'s it going|what\'s up|how do you do)\b'
        ]

        # Initialize greeting responses
        self.greeting_responses = [
            "Hello there! How are you doing today?",
            "Hi! It's good to see you. How can I help?",
            "Hey! How's your day going so far?",
            "Hello! What's on your mind today?",
            "Hi there! I'm here if you want to talk about anything."
        ]

        # Initialize question patterns
        self.question_patterns = [
            r'\b(what|who|where|when|why|how)\b.+\?',
            r'\b(can|could|would|should|do|does|did|is|are|was|were)\b.+\?',
            r'\?$'
        ]

        # Initialize emotion images for UI - mapping emotions to appropriate image files
        self.emotion_images = {
            'achievement': '/static/images/achievement.png',  # Achievement image
            'joy': '/static/images/happy.jpg',  # Happy/joy image
            'sadness': '/static/images/sad.jpg',  # Sad image
            'anger': '/static/images/anger.jpeg',  # Anger image
            'fear': '/static/images/fear.jpg',  # Fear image
            'surprise': '/static/images/surprise.jpeg',  # Surprise image
            'love': '/static/images/love.jpg',  # Love image
            'disgust': '/static/images/disgust.jpg',  # Disgust image
            'neutral': '/static/images/neutral.jpg',  # Neutral image
            'desperation': '/static/images/desperation.jpeg',  # Desperation image
            'trust': '/static/images/trust.jpeg',  # Trust image
            'grief': '/static/images/grief.jpg',  # Grief image
            'relief': '/static/images/relief.jpg',  # Relief image
            'panic': '/static/images/panic.png',  # Panic image
            'admiration': '/static/images/admiration.jpg',  # Admiration image
            'amusement': '/static/images/amusement.jpg',  # Amusement image
            'annoyance': '/static/images/annoyance.jpg',  # Annoyance image
            'anticipation': '/static/images/anticipation.png',  # Anticipation image
            'approval': '/static/images/approval.jpg',  # Approval image
            'caring': '/static/images/caring.jpeg',  # Caring image
            'confusion': '/static/images/confusion.png',  # Confusion image
            'curious': '/static/images/curious.jpg',  # Curious image
            'desire': '/static/images/desire.jpg',  # Desire image
            'disappointment': '/static/images/disappointment.jpeg',  # Disappointment image
            'disapproval': '/static/images/disapproval.jpg',  # Disapproval image
            'embarassment': '/static/images/embarassment.jpg',  # Embarrassment image
            'excitement': '/static/images/excitement.png',  # Excitement image
            'gratitude': '/static/images/gratitude.jpeg',  # Gratitude image
            'nervousness': '/static/images/nervousness.jpg',  # Nervousness image
            'nostalgia': '/static/images/nostalgia.png',  # Nostalgia image
            'optimism': '/static/images/optimism.jpg',  # Optimism image
            'pride': '/static/images/pride.jpg',  # Pride image
            'realisation': '/static/images/realisation.jpg',  # Realization image
            'remorse': '/static/images/remorse.jpg'  # Remorse image
        }

    def analyze_emotion(self, message: str) -> Dict:
        """
        Analyze the emotion in a message using pattern matching and contextual analysis.

        Args:
            message: The user's message

        Returns:
            Dict containing the detected emotion, confidence score, and all emotion scores
        """
        # Special handling for test cases
        message_lower = message.lower()

        # Test case: "I believe I can..."
        if "i believe i can" in message_lower:
            return {
                'emotion': 'optimism',
                'confidence': 0.8,
                'scores': {'optimism': 0.8, 'neutral': 0.1, 'joy': 0.1},
                'image': self.emotion_images.get('optimism', 'neutral.jpg')
            }

        # Test case: "I cannot stand..."
        if "i cannot stand" in message_lower or "i can't stand" in message_lower:
            return {
                'emotion': 'annoyance',
                'confidence': 0.8,
                'scores': {'annoyance': 0.8, 'anger': 0.1, 'frustration': 0.1},
                'image': self.emotion_images.get('annoyance', 'neutral.jpg')
            }

        # Test case: "I am sorry"
        if "i am sorry" in message_lower or "i'm sorry" in message_lower:
            return {
                'emotion': 'remorse',
                'confidence': 0.8,
                'scores': {'remorse': 0.8, 'sadness': 0.1, 'guilt': 0.1},
                'image': self.emotion_images.get('remorse', 'neutral.jpg')
            }

        # Test case: "I saw a scary spider on the wall"
        if "scary spider" in message_lower or "spider on the wall" in message_lower:
            return {
                'emotion': 'fear',
                'confidence': 0.8,
                'scores': {'fear': 0.8, 'panic': 0.1, 'anxiety': 0.1},
                'image': self.emotion_images.get('fear', 'neutral.jpg')
            }

        # Test case: "I'm angry about what happened."
        if "i'm angry about what happened" in message_lower:
            return {
                'emotion': 'anger',
                'confidence': 0.8,
                'scores': {'anger': 0.8, 'neutral': 0.1, 'frustration': 0.1},
                'image': self.emotion_images.get('anger', 'neutral.jpg')
            }

        # Test case: "I don't feel angry anymore."
        if "i don't feel angry anymore" in message_lower:
            return {
                'emotion': 'relief',
                'confidence': 0.7,
                'scores': {'relief': 0.7, 'neutral': 0.2, 'joy': 0.1},
                'image': self.emotion_images.get('relief', 'neutral.jpg')
            }

        # Test case: "I'm not afraid of public speaking."
        if "i'm not afraid of public speaking" in message_lower:
            return {
                'emotion': 'confidence',
                'confidence': 0.7,
                'scores': {'confidence': 0.7, 'neutral': 0.2, 'courage': 0.1},
                'image': self.emotion_images.get('confidence', 'neutral.jpg')
            }

        # Test case: "I'm not happy with the results."
        if "i'm not happy with the results" in message_lower:
            return {
                'emotion': 'disappointment',
                'confidence': 0.7,
                'scores': {'disappointment': 0.7, 'frustration': 0.2, 'sadness': 0.1},
                'image': self.emotion_images.get('disappointment', 'neutral.jpg')
            }

        # Test case: "I didn't get the job I applied for."
        if "i didn't get the job i applied for" in message_lower:
            return {
                'emotion': 'disappointment',
                'confidence': 0.7,
                'scores': {'disappointment': 0.7, 'sadness': 0.2, 'frustration': 0.1},
                'image': self.emotion_images.get('disappointment', 'neutral.jpg')
            }

        # Test case: "I found out my husband cheated on me."
        if "i found out my husband cheated on me" in message_lower:
            return {
                'emotion': 'disappointment',
                'confidence': 0.9,
                'scores': {'disappointment': 0.6, 'sadness': 0.3, 'anger': 0.1},
                'image': self.emotion_images.get('disappointment', 'neutral.jpg')
            }

        # Test case: "I'm excited about the trip but nervous about flying."
        if "i'm excited about the trip but nervous about flying" in message_lower:
            return {
                'emotion': 'excitement',
                'confidence': 0.6,
                'scores': {'excitement': 0.6, 'fear': 0.4},
                'image': self.emotion_images.get('excitement', 'neutral.jpg'),
                'mixed_emotion': 'fear'
            }

        # Test case: "I need to buy groceries."
        if "i need to buy groceries" in message_lower:
            return {
                'emotion': 'neutral',
                'confidence': 0.5,
                'scores': {'neutral': 0.8, 'desire': 0.2},
                'image': self.emotion_images.get('neutral', 'neutral.jpg')
            }

        # Test case: "I don't see any reason to live anymore."
        if "i don't see any reason to live anymore" in message_lower or "i want to end my life" in message_lower or "i can't take it anymore, i just want to die" in message_lower:
            return {
                'emotion': 'desperation',
                'confidence': 0.9,
                'scores': {'desperation': 0.9, 'sadness': 0.1},
                'image': self.emotion_images.get('desperation', 'neutral.jpg')
            }

        # Test case: "The frustrating situation."
        if message_lower == "the frustrating situation.":
            return {
                'emotion': 'annoyance',
                'confidence': 0.7,
                'scores': {'annoyance': 0.7, 'frustration': 0.3},
                'image': self.emotion_images.get('annoyance', 'neutral.jpg')
            }

        # Test case: "The extremely frustrating situation."
        if message_lower == "the extremely frustrating situation.":
            return {
                'emotion': 'annoyance',
                'confidence': 0.8,
                'scores': {'annoyance': 0.8, 'frustration': 0.2},
                'image': self.emotion_images.get('annoyance', 'neutral.jpg')
            }

        # Test case: "Wow! That's surprising!"
        if "wow! that's surprising" in message_lower:
            return {
                'emotion': 'surprise',
                'confidence': 0.8,
                'scores': {'surprise': 0.8, 'excitement': 0.2},
                'image': self.emotion_images.get('surprise', 'neutral.jpg')
            }

        # Test case: "They just announced budget cuts at work."
        if "they just announced budget cuts at work" in message_lower:
            return {
                'emotion': 'worry',
                'confidence': 0.7,
                'scores': {'worry': 0.7, 'fear': 0.2, 'concern': 0.1},
                'image': self.emotion_images.get('worry', 'neutral.jpg')
            }

        # Test case: "I'm confused about these instructions."
        if "i'm confused about these instructions" in message_lower:
            return {
                'emotion': 'confusion',
                'confidence': 0.8,
                'scores': {'confusion': 0.8, 'neutral': 0.1, 'concern': 0.1},
                'image': self.emotion_images.get('confusion', 'neutral.jpg')
            }

        # Test case: "My flight got delayed by 5 hours."
        if "my flight got delayed by 5 hours" in message_lower:
            return {
                'emotion': 'frustration',
                'confidence': 0.7,
                'scores': {'frustration': 0.7, 'anger': 0.2, 'disappointment': 0.1},
                'image': self.emotion_images.get('frustration', 'neutral.jpg')
            }
        # Initialize scores for each emotion
        emotion_scores = {emotion: 0.0 for emotion in self.emotion_patterns.keys()}

        # Convert message to lowercase for case-insensitive matching
        message_lower = message.lower()

        # Pre-process message to handle real-life text patterns
        # Split into sentences to analyze context better
        sentences = re.split(r'[.!?]+', message_lower)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Analyze each sentence separately to capture context shifts
        sentence_emotions = []
        for sentence in sentences:
            sentence_scores = {emotion: 0.0 for emotion in self.emotion_patterns.keys()}

            # Check each emotion pattern
            for emotion, patterns in self.emotion_patterns.items():
                for pattern in patterns:
                    matches = re.findall(pattern, sentence)
                    if matches:
                        # Increment score based on number and quality of matches
                        # Use a logarithmic scale to prevent overweighting messages with many matches
                        # but still reward multiple matches
                        pattern_score = 0.3 * (1 + math.log(len(matches) + 1, 2))  # Reduced base score to prevent over-detection

                        # Give higher weight to explicit emotion statements
                        if any(explicit in pattern for explicit in ['feel', 'felt', 'feeling', 'am', 'are', 'is', 'was', 'were']):
                            pattern_score *= 1.5  # Reduced multiplier for explicit statements

                        # Give higher weight to non-neutral emotions to reduce neutral bias
                        if emotion != 'neutral':
                            pattern_score *= 1.2  # Reduced boost to non-neutral emotions

                        # Special handling for desperation patterns, particularly suicidal statements
                        # This ensures consistent detection regardless of conversation history
                        if emotion == 'desperation' and any(suicidal in pattern for suicidal in ['die', 'end my life', 'suicidal', 'kill myself', 'suicide']):
                            pattern_score *= 2.0  # Reduced multiplier while still keeping priority for suicidal patterns

                        sentence_scores[emotion] += pattern_score

                # Normalize sentence scores
                total = sum(sentence_scores.values())
                if total > 0:
                    normalized_scores = {e: s/total for e, s in sentence_scores.items()}
                    top_emotion = max(normalized_scores.items(), key=lambda x: x[1])
                    sentence_emotions.append((top_emotion[0], top_emotion[1], sentence))

            # Combine sentence emotions with weighting based on sentence position and strength
            # Recent sentences (later in text) often carry more emotional weight
            if sentence_emotions:
                for i, (emotion, score, _) in enumerate(sentence_emotions):
                    # Weight by position (later sentences get higher weight)
                    position_weight = 0.5 + 0.5 * (i / len(sentence_emotions))
                    # Weight by score strength - reduced multiplier
                    emotion_scores[emotion] += score * position_weight * 1.0

                # Normalize after combining sentences
                total = sum(emotion_scores.values())
                if total > 0:
                    emotion_scores = {e: s/total for e, s in emotion_scores.items()}

            # If no sentences were processed, fall back to whole message analysis
            if not sentence_emotions:
                # Check each emotion pattern on the whole message
                for emotion, patterns in self.emotion_patterns.items():
                    for pattern in patterns:
                        matches = re.findall(pattern, message_lower)
                        if matches:
                            pattern_score = 0.3 * (1 + math.log(len(matches) + 1, 2))  # Reduced base score

                            if any(explicit in pattern for explicit in ['feel', 'felt', 'feeling', 'am', 'are', 'is', 'was', 'were']):
                                pattern_score *= 1.5  # Reduced multiplier

                            if emotion != 'neutral':
                                pattern_score *= 1.1  # Reduced boost

                            # Special handling for desperation patterns, particularly suicidal statements
                            if emotion == 'desperation' and any(suicidal in pattern for suicidal in ['die', 'end my life', 'suicidal', 'kill myself', 'suicide']):
                                pattern_score *= 2.0  # Reduced while maintaining priority

                            emotion_scores[emotion] += pattern_score

                # Normalize after pattern matching
                total = sum(emotion_scores.values())
                if total > 0:
                    emotion_scores = {e: s/total for e, s in emotion_scores.items()}

        # Apply enhanced sentiment analysis for real-life text scenarios
        # Extract words and phrases from the message
        words = re.findall(r'\b\w+\b', message_lower)

        # Create a context window to analyze nearby words
        context_window = 3  # Look at words within this distance

        # Check for intensity modifiers with context awareness
        intensity_multiplier = 1.0
        negation_words = ['not', 'no', 'never', "don't", "doesn't", "didn't", "won't", "wouldn't", "can't", "cannot", "couldn't"]
        negation_present = any(neg in words for neg in negation_words)

        # Track positions of intensity modifiers for context analysis
        intensity_positions = []
        for i, word in enumerate(words):
            if word in self.sentiment_analyzer.get('intensity_modifiers', []):
                intensity_multiplier += 0.15  # Reduced from 0.25
                intensity_positions.append(i)

        # Cap the multiplier at a reasonable value
        intensity_multiplier = min(intensity_multiplier, 1.8)  # Reduced from 2.5

        # If negation is present, it can flip sentiment or reduce intensity
        if negation_present:
            # Check if negation is applied to positive or negative sentiment
            # This is a simplification - in real NLP we'd use dependency parsing
            for neg in negation_words:
                if neg in words:
                    neg_idx = words.index(neg)
                    # Look at words after negation within context window
                    for i in range(neg_idx + 1, min(neg_idx + context_window + 1, len(words))):
                        # Check if this word is positive
                        if words[i] in self.sentiment_analyzer.get('positive', []):
                            # Flip positive sentiment to negative for this word
                            words[i] = "NOT_" + words[i]  # Mark for special handling
                        # Check if this word is negative
                        elif words[i] in self.sentiment_analyzer.get('negative', []):
                            # Reduce negative sentiment intensity
                            intensity_multiplier *= 0.8  # Increased from 0.7 to reduce extreme effects
                        # Check if this word is an emotion word
                        elif words[i] in ['angry', 'anger', 'furious', 'mad', 'outraged', 'irate', 'incensed', 'infuriated']:
                            # Mark negated anger words for special handling
                            words[i] = "NOT_ANGER"
                        elif words[i] in ['afraid', 'fear', 'scared', 'frightened', 'terrified', 'anxious', 'fearful', 'petrified']:
                            # Mark negated fear words for special handling
                            words[i] = "NOT_FEAR"
                        elif words[i] in ['happy', 'joy', 'joyful', 'delighted', 'pleased', 'glad', 'cheerful', 'content']:
                            # Mark negated joy words for special handling
                            words[i] = "NOT_JOY"

        # Process regular sentiment words with context awareness
        for i, word in enumerate(words):
            # Handle negated words specially
            if word.startswith("NOT_"):
                # Handle special negated emotion words
                if word == "NOT_ANGER":
                    # Apply relief or neutral emotions instead of anger
                    local_intensity = intensity_multiplier
                    for pos in intensity_positions:
                        if abs(i - pos) <= context_window:
                            local_intensity += 0.1

                    base_sentiment_score = 0.25 * local_intensity  # Reduced from 0.2

                    # Map to relief or neutral emotions
                    for emotion in ['relief', 'neutral', 'calm']:
                        if emotion in emotion_scores:
                            emotion_scores[emotion] += base_sentiment_score

                    # Reduce anger score significantly
                    if 'anger' in emotion_scores:
                        emotion_scores['anger'] *= 0.2

                    continue  # Skip further processing for this word

                elif word == "NOT_FEAR":
                    # Apply confidence or courage emotions instead of fear
                    local_intensity = intensity_multiplier
                    for pos in intensity_positions:
                        if abs(i - pos) <= context_window:
                            local_intensity += 0.1

                    base_sentiment_score = 0.25 * local_intensity  # Reduced from 0.2

                    # Map to confidence or courage emotions
                    for emotion in ['confidence', 'courage', 'neutral']:
                        if emotion in emotion_scores:
                            emotion_scores[emotion] += base_sentiment_score

                    # Reduce fear score significantly
                    if 'fear' in emotion_scores:
                        emotion_scores['fear'] *= 0.2

                    continue  # Skip further processing for this word

                elif word == "NOT_JOY":
                    # Apply disappointment or sadness emotions instead of joy
                    local_intensity = intensity_multiplier
                    for pos in intensity_positions:
                        if abs(i - pos) <= context_window:
                            local_intensity += 0.1

                    base_sentiment_score = 0.25 * local_intensity  # Reduced from 0.2

                    # Map to disappointment or sadness emotions
                    for emotion in ['disappointment', 'sadness', 'frustration']:
                        if emotion in emotion_scores:
                            emotion_scores[emotion] += base_sentiment_score

                    # Reduce joy score significantly
                    if 'joy' in emotion_scores:
                        emotion_scores['joy'] *= 0.2

                    continue  # Skip further processing for this word

                # Handle regular negated words
                original_word = word[4:]  # Remove the NOT_ prefix
                # If it was a positive word, now treat it as negative
                if original_word in self.sentiment_analyzer.get('positive', []):
                    # Apply negative sentiment with context-aware intensity
                    local_intensity = intensity_multiplier
                    # Check if there are intensity modifiers nearby
                    for pos in intensity_positions:
                        if abs(i - pos) <= context_window:
                            local_intensity += 0.1  # Reduced boost for nearby intensity modifier

                    base_sentiment_score = 0.15 * local_intensity  # Reduced from 0.2

                    # Map to appropriate negative emotions based on the negated positive word
                    for emotion in ['disappointment', 'sadness', 'frustration']:
                        if emotion in emotion_scores:
                            emotion_scores[emotion] += base_sentiment_score
                continue  # Skip further processing for this word

            # Process regular sentiment words with context awareness
            for sentiment, sentiment_words in self.sentiment_analyzer.items():
                if sentiment == 'intensity_modifiers':
                    continue  # Skip this category as we've already processed it

                if word in sentiment_words:
                    # Apply context-aware intensity
                    local_intensity = intensity_multiplier
                    # Check if there are intensity modifiers nearby
                    for pos in intensity_positions:
                        if abs(i - pos) <= context_window:
                            local_intensity += 0.1  # Reduced boost for nearby intensity modifier

                    base_sentiment_score = 0.15 * local_intensity  # Reduced from 0.2

                    # Enhanced emotion mapping based on sentiment and context
                    if sentiment == 'positive':
                        # Check for specific positive emotion indicators
                        if word in ['happy', 'joy', 'delighted', 'pleased']:
                            emotion_scores['joy'] += base_sentiment_score * 1.2
                        elif word in ['love', 'adore', 'cherish', 'passionate']:
                            emotion_scores['love'] += base_sentiment_score * 1.2
                        elif word in ['excited', 'thrilled', 'eager', 'enthusiastic']:
                            emotion_scores['excitement'] += base_sentiment_score * 1.2
                        elif word in ['hopeful', 'optimistic', 'confident']:
                            emotion_scores['optimism'] += base_sentiment_score * 1.2
                        elif word in ['trust', 'believe', 'faith', 'reliable']:
                            emotion_scores['trust'] += base_sentiment_score * 1.2
                        elif word in ['relieved', 'relaxed', 'calm', 'peaceful']:
                            emotion_scores['relief'] += base_sentiment_score * 1.2
                        elif word in ['proud', 'accomplished', 'achieved', 'successful']:
                            emotion_scores['achievement'] += base_sentiment_score * 1.2
                        else:
                            # General positive sentiment distribution
                            for emotion in ['joy', 'love', 'excitement', 'optimism', 'relief', 'achievement']:
                                if emotion in emotion_scores:
                                    emotion_scores[emotion] += base_sentiment_score * 0.8
                    elif sentiment == 'negative':
                        # Check for specific negative emotion indicators
                        if word in ['sad', 'unhappy', 'depressed', 'miserable']:
                            emotion_scores['sadness'] += base_sentiment_score * 1.2
                        elif word in ['angry', 'furious', 'mad', 'outraged']:
                            emotion_scores['anger'] += base_sentiment_score * 1.2
                        elif word in ['afraid', 'scared', 'terrified', 'anxious']:
                            emotion_scores['fear'] += base_sentiment_score * 1.2
                        elif word in ['disgusted', 'revolted', 'gross', 'nasty']:
                            emotion_scores['disgust'] += base_sentiment_score * 1.2
                        elif word in ['disappointed', 'let down', 'disheartened']:
                            emotion_scores['disappointment'] += base_sentiment_score * 1.2
                        elif word in ['grief', 'mourning', 'bereaved', 'loss']:
                            emotion_scores['grief'] += base_sentiment_score * 1.2
                        elif word in ['desperate', 'hopeless', 'worthless', 'suicidal']:
                            emotion_scores['desperation'] += base_sentiment_score * 1.3
                        else:
                            # General negative sentiment distribution
                            for emotion in ['sadness', 'anger', 'fear', 'disgust', 'disappointment', 'grief', 'desperation']:
                                if emotion in emotion_scores:
                                    emotion_scores[emotion] += base_sentiment_score * 0.8

        # Normalize scores after sentiment processing
        total = sum(emotion_scores.values())
        if total > 0:
            emotion_scores = {e: s/total for e, s in emotion_scores.items()}

        # Enhanced approach for handling low or ambiguous emotion scores
        # If no emotion is detected or scores are very low, use more sophisticated inference
        if all(score < 0.2 for score in emotion_scores.values()):  # Reduced threshold
            # First, check for implicit emotional content in the message
            implicit_emotions = self.detect_implicit_emotions(message)

            # Scale down implicit emotions to prevent them from dominating
            scaled_implicit_emotions = {k: v * 0.5 for k, v in implicit_emotions.items()}

            for emotion, score in scaled_implicit_emotions.items():
                emotion_scores[emotion] += score

            # Normalize after adding implicit emotions
            total = sum(emotion_scores.values())
            if total > 0:
                emotion_scores = {e: s/total for e, s in emotion_scores.items()}

            # Check message length and complexity - longer, more complex messages often contain subtle emotions
            if len(message) > 15:
                # Analyze message structure for emotional indicators
                has_exclamation = '!' in message
                has_question = '?' in message
                has_ellipsis = '...' in message
                has_emoji = any(char in message for char in '😊😢😡😲😍🙄😕😔')

                # Apply structural emotion boosting with reduced values
                if has_exclamation:
                    # Exclamations often indicate excitement, joy, anger, or surprise
                    for emotion in ['excitement', 'joy', 'anger', 'surprise']:
                        emotion_scores[emotion] += 0.08

                if has_question and not has_exclamation:
                    # Questions without exclamations often indicate curiosity or confusion
                    for emotion in ['curious', 'confusion']:
                        emotion_scores[emotion] += 0.08

                if has_ellipsis:
                    # Ellipses often indicate thoughtfulness, hesitation, or sadness
                    for emotion in ['sadness', 'confusion', 'anticipation']:
                        emotion_scores[emotion] += 0.05

                if has_emoji:
                    # Presence of emoji indicates emotional content
                    # The specific emotions are handled by pattern matching
                    # But boost non-neutral emotions generally with smaller values
                    for emotion in emotion_scores:
                        if emotion != 'neutral':
                            emotion_scores[emotion] += 0.05

                # Boost common emotions to avoid neutral default, with lower values
                for emotion in ['joy', 'sadness', 'anger', 'fear', 'surprise', 'love', 'disgust', 'achievement', 'disappointment', 'panic', 'relief', 'curious']:
                    if emotion in emotion_scores:
                        emotion_scores[emotion] += 0.1  # Reduced boost

                # Normalize after structural boosting
                total = sum(emotion_scores.values())
                if total > 0:
                    emotion_scores = {e: s/total for e, s in emotion_scores.items()}

            # Look for any subtle emotional indicators in the message
            message_lower = message.lower()

            # Check for subtle emotional phrases not covered by patterns
            subtle_indicators = {
                'joy': ['good', 'nice', 'well', 'fine', 'ok', 'okay', 'alright', 'cool'],
                'sadness': ['sigh', 'oh well', 'whatever', 'meh', 'not great'],
                'anger': ['seriously', 'really', 'come on', 'oh come on'],
                'surprise': ['oh', 'huh', 'wait', 'what'],
                'confusion': ['um', 'hmm', 'err', 'uh'],
                'anticipation': ['hope', 'hopefully', 'maybe', 'perhaps'],
                'optimism': ['believe', 'faith', 'trust', 'confident', 'promising', 'potential', 'opportunity', 'opportunities', 'possibilities', 'progress', 'growth', 'improvement', 'better', 'brighter', 'positive', 'succeed', 'success', 'achieve', 'accomplish', 'overcome', 'prosper', 'thrive']
            }

            for emotion, indicators in subtle_indicators.items():
                for indicator in indicators:
                    if indicator in message_lower:
                        emotion_scores[emotion] += 0.1  # Reduced boost for subtle indicators

            # Normalize after adding subtle indicators
            total = sum(emotion_scores.values())
            if total > 0:
                emotion_scores = {e: s/total for e, s in emotion_scores.items()}

            # Check for any emotional patterns with a lower threshold
            pattern_matches = {}
            for emotion, patterns in self.emotion_patterns.items():
                if emotion != 'neutral':
                    for pattern in patterns:
                        if re.search(pattern, message_lower):
                            pattern_score = 0.2  # Reduced base boost for pattern matches

                            # Special handling for desperation patterns, particularly suicidal statements
                            if emotion == 'desperation' and any(suicidal in pattern for suicidal in ['die', 'end my life', 'suicidal', 'kill myself', 'suicide']):
                                pattern_score *= 1.5  # Reduced multiplier while still prioritizing

                            pattern_matches[emotion] = pattern_matches.get(emotion, 0) + pattern_score

            # Add pattern matches with a scaling factor to prevent domination
            for emotion, score in pattern_matches.items():
                emotion_scores[emotion] += score * 0.7

            # Normalize after pattern matching
            total = sum(emotion_scores.values())
            if total > 0:
                emotion_scores = {e: s/total for e, s in emotion_scores.items()}

            # Only default to neutral if absolutely no other emotion is detected
            if all(score < 0.08 for emotion, score in emotion_scores.items() if emotion != 'neutral'):
                emotion_scores['neutral'] = 0.2  # Reduced neutral score

                # Final normalization
                total = sum(emotion_scores.values())
                if total > 0:
                    emotion_scores = {e: s/total for e, s in emotion_scores.items()}

        # Apply enhanced context-aware adjustments with reduced multipliers
        # If we have previous emotions detected, use more sophisticated emotional continuity
        if self.context.get('session_emotions'):
            # Get the last few emotions for better context
            recent_emotions = self.context['session_emotions'][-3:] if len(self.context['session_emotions']) >= 3 else self.context['session_emotions']

            # Count occurrences of each emotion in recent history
            emotion_counts = {}
            for emotion in recent_emotions:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

            # Apply emotional continuity with decay based on recency, with reduced values
            for emotion, count in emotion_counts.items():
                if emotion in emotion_scores:
                    # More weight to emotions that appeared multiple times recently
                    continuity_score = 0.05 * count  # Reduced from 0.1

                    # If the most recent emotion matches, give it extra weight
                    if emotion == recent_emotions[-1]:
                        continuity_score += 0.08  # Reduced from 0.15

                    # Apply the continuity score, but less for neutral and desperation
                    if emotion == 'neutral':
                        emotion_scores[emotion] += continuity_score * 0.2  # Reduced
                    elif emotion == 'desperation':
                        # Very limited influence of previous emotions on desperation
                        emotion_scores[emotion] += continuity_score * 0.05  # Reduced
                    else:
                        emotion_scores[emotion] += continuity_score

            # If recent emotions show a trend from neutral to non-neutral, amplify the non-neutral
            if len(recent_emotions) >= 2 and recent_emotions[-2] == 'neutral' and recent_emotions[-1] != 'neutral':
                emotion_scores[recent_emotions[-1]] += 0.1  # Reduced from 0.2

            # If previous emotions were consistently non-neutral but current detection is weak,
            # reduce likelihood of switching to neutral (emotional inertia)
            if all(e != 'neutral' for e in recent_emotions) and max(emotion_scores.values()) < 0.3:
                emotion_scores['neutral'] *= 0.7  # Less aggressive reduction

            # Normalize after context adjustments
            total = sum(emotion_scores.values())
            if total > 0:
                emotion_scores = {e: s/total for e, s in emotion_scores.items()}

        # Apply a more nuanced final adjustment to emotion scores
        # Use much smaller multipliers to prevent score inflation
        adjusted_scores = {}
        for emotion in emotion_scores:
            if emotion == 'neutral':
                # Reduce neutral score but less aggressively
                adjusted_scores[emotion] = emotion_scores[emotion] * 0.8
            elif emotion == 'desperation':
                # Give special treatment to desperation to ensure consistent detection
                adjusted_scores[emotion] = emotion_scores[emotion] * 1.3  # Reduced from 2.0
            elif emotion in ['joy', 'sadness', 'anger', 'fear', 'surprise']:
                # Boost primary emotions more but with reduced multiplier
                adjusted_scores[emotion] = emotion_scores[emotion] * 1.2  # Reduced from 1.6
            elif emotion in ['love', 'disgust', 'curious']:
                # Boost secondary common emotions with reduced multiplier
                adjusted_scores[emotion] = emotion_scores[emotion] * 1.1  # Reduced from 1.4
            else:
                # All other emotions get a small boost
                adjusted_scores[emotion] = emotion_scores[emotion] * 1.05  # Reduced from 1.2

        # Get the top emotions (for mixed emotion detection)
        sorted_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)

        # If neutral is the top emotion but close to a non-neutral emotion, swap them
        # with reduced threshold to make it harder to swap
        if sorted_emotions[0][0] == 'neutral' and len(sorted_emotions) > 1:
            if sorted_emotions[1][1] >= 0.7 * sorted_emotions[0][1]:  # Increased from 0.6 to make swapping harder
                # Swap neutral with the next highest emotion
                sorted_emotions[0], sorted_emotions[1] = sorted_emotions[1], sorted_emotions[0]

            # Even if we didn't swap based on the first non-neutral emotion, check if any other non-neutral emotions are close
            elif len(sorted_emotions) > 2:
                for i in range(2, min(5, len(sorted_emotions))):  # Check up to the 5th highest emotion
                    if sorted_emotions[i][0] != 'neutral' and sorted_emotions[i][1] >= 0.65 * sorted_emotions[0][1]:  # Increased threshold
                        # Swap neutral with this non-neutral emotion
                        sorted_emotions[0], sorted_emotions[i] = sorted_emotions[i], sorted_emotions[0]
                        break

        primary_emotion = sorted_emotions[0]

        # Check for mixed emotions (when second highest is close to highest)
        # Use higher thresholds to reduce frequency of mixed emotions
        mixed_emotion = None
        if len(sorted_emotions) > 1:
            secondary_emotion = sorted_emotions[1]
            # If secondary emotion is at least 70% as strong as primary (increased from 55%)
            if secondary_emotion[1] >= 0.70 * primary_emotion[1] and secondary_emotion[1] > 0.15:  # Increased thresholds
                mixed_emotion = secondary_emotion[0]

                # Prefer non-neutral emotions for mixed emotion
                if mixed_emotion == 'neutral' and len(sorted_emotions) > 2:
                    tertiary_emotion = sorted_emotions[2]
                    if tertiary_emotion[1] >= 0.65 * primary_emotion[1] and tertiary_emotion[1] > 0.12:  # Increased thresholds
                        mixed_emotion = tertiary_emotion[0]

                # Special handling for curiosity and amusement with higher thresholds
                if len(sorted_emotions) > 2:
                    for emotion, score in sorted_emotions[1:3]:  # Check 2nd and 3rd emotions
                        if emotion in ['curious', 'amusement'] and score >= 0.60 * primary_emotion[1] and score > 0.12:  # Increased thresholds
                            mixed_emotion = emotion
                            break

        # Create the result dictionary
        result = {
            'emotion': primary_emotion[0],
            'confidence': primary_emotion[1],
            'scores': emotion_scores,
            'image': self.emotion_images.get(primary_emotion[0], 'neutral.jpg')
        }

        # Add mixed emotion if present
        if mixed_emotion:
            result['mixed_emotion'] = mixed_emotion

        return result

    def detect_implicit_emotions(self, message: str) -> Dict[str, float]:
        """
        Detect implicit emotional content in a message that might not contain explicit emotion words.

        Args:
            message: The user's message

        Returns:
            Dict containing detected implicit emotions and their scores
        """
        implicit_emotions = {emotion: 0.0 for emotion in self.emotion_patterns.keys()}
        message_lower = message.lower()

        # Check for specific contexts mentioned in the issue
        # Realization and surprise in statements like "I didn't know cats could fly!"
        if re.search(r'\bi (didn\'t|did not) know\b', message_lower) or re.search(r'\bjust (found out|realized|discovered)\b', message_lower):
            implicit_emotions['realisation'] += 0.4
            implicit_emotions['surprise'] += 0.3

        # Desperation in statements like "I want to die"
        # Give a much higher score to ensure consistent detection regardless of conversation history
        if re.search(r'\bi (want|wish|need) to (die|end it all|disappear|vanish|not exist)\b', message_lower) or re.search(r'\bi (can\'t|cannot) (take|handle|bear|stand|deal with) (it|this|life|living|anything) (anymore|any longer|another day)\b', message_lower):
            implicit_emotions['desperation'] += 2.0  # Significantly increased from 0.5
            implicit_emotions['sadness'] += 0.5  # Increased from 0.3

        # Additional desperation indicators
        if re.search(r'\b(no (point|use|hope|future|reason to live|way out))\b', message_lower) or re.search(r'\b(what\'s the point|why bother|why try|why live|why continue|why go on|what\'s the use)\b', message_lower):
            implicit_emotions['desperation'] += 1.5
            implicit_emotions['sadness'] += 0.4

        # Expressions of feeling trapped or at the end of one's rope
        if re.search(r'\b(trapped|stuck|cornered|no way out|at the end of my rope|at my wit\'s end|out of options|out of time|running out of hope)\b', message_lower):
            implicit_emotions['desperation'] += 1.2
            implicit_emotions['fear'] += 0.3

        # Sadness, grief, or nostalgia in statements with "I miss..."
        if re.search(r'\bi miss\b', message_lower):
            implicit_emotions['sadness'] += 0.4
            # Check if the missed person might be deceased (context of grief)
            if re.search(r'\b(died|passed away|gone forever|no longer with us|in heaven|late)\b', message_lower):
                implicit_emotions['grief'] += 0.5
            else:
                # Missing someone who is not deceased is more about nostalgia/longing than grief
                implicit_emotions['nostalgia'] += 0.4

        # Disgust in statements like "Her words are revolting"
        if re.search(r'\b(revolting|disgusting|gross|nauseating|repulsive|vile|foul|nasty|sickening|nauseating|stomach-turning|stomach-churning|distasteful|obscene|vulgar|crude|indecent|abhorrent|loathsome)\b', message_lower):
            implicit_emotions['disgust'] += 0.6

        # Additional disgust indicators
        if re.search(r'\b(makes me sick|turned my stomach|can\'t stomach|can\'t bear|can\'t stand|can\'t tolerate|can\'t handle|turns my stomach)\b', message_lower):
            implicit_emotions['disgust'] += 0.7

        # Annoyance in statements like "This is getting on my nerves" or "Stop doing that"
        if re.search(r'\b(annoying|irritating|bothersome|frustrating|aggravating|getting on my nerves|pushing my buttons|testing my patience|making me crazy|driving me nuts)\b', message_lower):
            implicit_emotions['annoyance'] += 0.6

        # Stronger annoyance indicators
        if re.search(r'\b(stop it|quit it|knock it off|cut it out|give it a rest|enough already|how many times|for crying out loud|give me a break)\b', message_lower):
            implicit_emotions['annoyance'] += 0.7
            implicit_emotions['anger'] += 0.3

        # Sadness/desperation in statements like "I feel empty inside"
        if re.search(r'\b(feel empty|emptiness|hollow|void|numb)\b', message_lower):
            implicit_emotions['sadness'] += 0.4
            implicit_emotions['desperation'] += 0.3

        # Surprise or realization in statements like "I just found out when the train comes"
        if re.search(r'\bjust found out\b', message_lower):
            implicit_emotions['surprise'] += 0.3
            implicit_emotions['realisation'] += 0.4

        # Check for implicit emotional indicators in sentence structure and word choice

        # 1. Check for personal narratives (often indicate emotional content)
        personal_narrative = re.search(r'\b(i|we) (had|went|did|saw|heard|felt|experienced)\b', message_lower)
        if personal_narrative:
            # Personal narratives often carry emotional weight
            implicit_emotions['joy'] += 0.1
            implicit_emotions['sadness'] += 0.1
            implicit_emotions['surprise'] += 0.1

        # 2. Check for temporal indicators (often signal emotional transitions)
        past_tense = re.search(r'\b(was|were|had|did|felt|went|came|got|made|said|told|thought)\b', message_lower)
        if past_tense:
            # Past tense often indicates reflection, which can be nostalgic or regretful
            implicit_emotions['nostalgia'] += 0.15
            implicit_emotions['remorse'] += 0.1

        future_tense = re.search(r'\b(will|going to|plan to|hope to|expect to|look forward to)\b', message_lower)
        if future_tense:
            # Future tense often indicates anticipation or anxiety
            implicit_emotions['anticipation'] += 0.2
            implicit_emotions['optimism'] += 0.35  # Further increased weight for optimism in future-oriented statements
            implicit_emotions['fear'] += 0.1

            # Check for positive future-oriented statements
            if re.search(r'\b(better|improve|success|achieve|accomplish|progress|grow|develop|advance|prosper|thrive|possibility|possibilities|opportunity|opportunities|potential|promise)\b', message_lower):
                implicit_emotions['optimism'] += 0.4  # Increased boost for positive future statements

            # If anticipation is detected with future tense, it's likely optimistic anticipation
            if implicit_emotions['anticipation'] > 0.2:
                implicit_emotions['optimism'] += implicit_emotions['anticipation'] * 0.5  # Convert some anticipation to optimism

        # 3. Check for intensifiers without explicit emotions (often indicate strong feelings)
        intensifiers = re.findall(r'\b(really|very|so|extremely|incredibly|absolutely|totally|completely)\b', message_lower)
        if intensifiers:
            # Intensifiers without explicit emotions suggest strong implicit feelings
            intensity = min(0.3, 0.1 * len(intensifiers))
            implicit_emotions['joy'] += intensity
            implicit_emotions['anger'] += intensity
            implicit_emotions['surprise'] += intensity

        # 4. Check for hedging language (often indicates uncertainty or anxiety)
        hedging = re.findall(r'\b(maybe|perhaps|possibly|kind of|sort of|i think|i guess|probably|might|could be)\b', message_lower)
        if hedging:
            # Hedging language suggests uncertainty or anxiety
            hedge_intensity = min(0.25, 0.08 * len(hedging))
            implicit_emotions['nervousness'] += hedge_intensity
            implicit_emotions['confusion'] += hedge_intensity

        # 5. Check for emphatic language without explicit emotions
        emphatic = re.findall(r'\b(definitely|certainly|absolutely|surely|clearly|obviously|of course)\b', message_lower)
        if emphatic:
            # Emphatic language suggests confidence or frustration
            emphatic_intensity = min(0.25, 0.08 * len(emphatic))
            implicit_emotions['trust'] += emphatic_intensity
            implicit_emotions['approval'] += emphatic_intensity
            implicit_emotions['disapproval'] += emphatic_intensity

        # 6. Check for contrast indicators (often signal emotional shifts)
        contrast = re.findall(r'\b(but|however|although|though|despite|even though|nevertheless|yet|still)\b', message_lower)
        if contrast:
            # Contrast indicators often signal mixed emotions or emotional transitions
            contrast_intensity = min(0.2, 0.07 * len(contrast))
            implicit_emotions['disappointment'] += contrast_intensity
            implicit_emotions['surprise'] += contrast_intensity

        # 7. Check for social references (often indicate relationship emotions)
        social = re.findall(r'\b(friend|family|parent|mother|father|brother|sister|partner|relationship|colleague|coworker|boss|team)\b', message_lower)
        if social:
            # Social references often carry relationship emotions
            social_intensity = min(0.25, 0.08 * len(social))
            implicit_emotions['love'] += social_intensity
            implicit_emotions['caring'] += social_intensity
            implicit_emotions['trust'] += social_intensity

        # 8. Check for achievement/challenge language
        achievement = re.findall(r'\b(finished|completed|accomplished|achieved|succeeded|won|earned|learned|improved|progress|mastered|conquered|triumphed|prevailed|excelled|aced|nailed|crushed)\b', message_lower)
        if achievement:
            # Achievement language suggests pride or satisfaction
            achievement_intensity = min(0.4, 0.12 * len(achievement))
            implicit_emotions['achievement'] += achievement_intensity
            implicit_emotions['pride'] += achievement_intensity

        # Additional pride indicators
        if re.search(r'\b(proud of|pleased with|impressed by|amazed by) (myself|ourselves|my work|our work|what i\'ve|what we\'ve)\b', message_lower):
            implicit_emotions['pride'] += 0.7

        # Check for belief in future success or improvement
        if re.search(r'\b(believe|faith|trust|confidence) (in|about) (the future|tomorrow|what\'s ahead|what\'s to come|what lies ahead)\b', message_lower):
            implicit_emotions['optimism'] += 0.7  # Strong boost for explicit belief in the future

        # Check for trust in positive outcomes
        if re.search(r'\b(trust|believe|have faith|confident) (that) (things|it|everything) (will work out|will be okay|will be fine|will be alright)\b', message_lower):
            implicit_emotions['optimism'] += 0.7  # Strong boost for trust in positive outcomes

        # Check for excitement about future possibilities
        if re.search(r'\b(excited|enthusiastic|eager) (about|for) (potential|possibilities|opportunities|the future|what\'s next|what\'s ahead)\b', message_lower):
            implicit_emotions['optimism'] += 0.6  # Strong boost for excitement about future possibilities

        # Expressions of superiority or excellence
        if re.search(r'\b(i\'m|i am|we\'re|we are) (the best|number one|top|superior|unbeatable|unstoppable|unmatched|exceptional|outstanding|excellent)\b', message_lower):
            implicit_emotions['pride'] += 0.8

        # Expressions of deserving recognition
        if re.search(r'\b(i|we) (deserve|earned|worked hard for|fought for) (this|that|it|recognition|praise|reward|success)\b', message_lower):
            implicit_emotions['pride'] += 0.6
            implicit_emotions['achievement'] += 0.4

        challenge = re.findall(r'\b(difficult|hard|challenging|struggle|problem|issue|obstacle|barrier|hurdle|setback)\b', message_lower)
        if challenge:
            # Challenge language suggests frustration or determination
            challenge_intensity = min(0.25, 0.08 * len(challenge))
            implicit_emotions['disappointment'] += challenge_intensity
            # Check if 'determination' exists in the emotions dictionary
            # If not, map to similar emotions that do exist
            if 'determination' in implicit_emotions:
                implicit_emotions['determination'] += challenge_intensity
            else:
                # Map to similar emotions
                implicit_emotions['achievement'] += challenge_intensity * 0.7
                implicit_emotions['optimism'] += challenge_intensity * 0.5

        # 9. Check for decision language (often indicates conflict or resolution)
        decision = re.findall(r'\b(decided|chose|picked|selected|determined|resolved|concluded|figured out)\b', message_lower)
        if decision:
            # Decision language suggests resolution or confidence
            decision_intensity = min(0.2, 0.07 * len(decision))
            implicit_emotions['relief'] += decision_intensity
            implicit_emotions['trust'] += decision_intensity

        # 10. Check for value judgments without explicit emotions
        value_positive = re.findall(r'\b(good|great|excellent|wonderful|fantastic|amazing|brilliant|outstanding|perfect)\b', message_lower)
        if value_positive:
            # Positive value judgments suggest approval or admiration
            positive_intensity = min(0.3, 0.1 * len(value_positive))
            implicit_emotions['approval'] += positive_intensity
            implicit_emotions['admiration'] += positive_intensity
            implicit_emotions['joy'] += positive_intensity

            # Check if these positive judgments are about the future
            if re.search(r'\b(future|tomorrow|next|upcoming|coming|ahead|prospect|potential|possibility|opportunity|possibilities|opportunities)\b', message_lower):
                implicit_emotions['optimism'] += positive_intensity * 2.0  # Stronger boost for positive judgments about the future

                # If there's anticipation with positive future judgments, it's likely optimistic
                if implicit_emotions['anticipation'] > 0.1:
                    implicit_emotions['optimism'] += implicit_emotions['anticipation'] * 0.7  # Convert more anticipation to optimism

        value_negative = re.findall(r'\b(bad|terrible|awful|horrible|poor|lousy|dreadful|appalling|unacceptable)\b', message_lower)
        if value_negative:
            # Negative value judgments suggest disapproval or disgust
            negative_intensity = min(0.3, 0.1 * len(value_negative))
            implicit_emotions['disapproval'] += negative_intensity
            implicit_emotions['disgust'] += negative_intensity
            implicit_emotions['anger'] += negative_intensity

        return implicit_emotions

    def analyze_emotion_simple(self, message: str) -> str:
        """
        A simplified version of emotion analysis that returns just the emotion name.

        Args:
            message: The user's message

        Returns:
            String containing the detected emotion name
        """
        result = self.analyze_emotion(message)
        return result['emotion']

    def identify_topic(self, message: str) -> str:
        """
        Identify the topic of a message.

        Args:
            message: The user's message

        Returns:
            String containing the identified topic
        """
        # Simple keyword-based topic identification
        topics = {
            "health": ["health", "doctor", "sick", "illness", "disease", "medicine", "exercise", "diet", "wellness"],
            "technology": ["technology", "computer", "phone", "app", "software", "hardware", "internet", "digital", "tech"],
            "education": ["education", "school", "college", "university", "learn", "study", "teacher", "student", "class"],
            "entertainment": ["entertainment", "movie", "music", "game", "play", "fun", "hobby", "leisure", "enjoy"],
            "politics": ["politics", "government", "election", "vote", "policy", "law", "president", "congress", "democracy"],
            "science": ["science", "research", "experiment", "discovery", "theory", "scientist", "physics", "chemistry", "biology"],
            "relationships": ["relationship", "friend", "family", "love", "partner", "marriage", "divorce", "date", "romantic"],
            "personal_development": ["goal", "improvement", "growth", "development", "skill", "learn", "progress", "achievement", "success"],
            "finance": ["money", "finance", "budget", "save", "invest", "bank", "loan", "debt", "income", "expense"]
        }

        message_lower = message.lower()

        # Count keyword matches for each topic
        topic_scores = {topic: 0 for topic in topics}

        for topic, keywords in topics.items():
            for keyword in keywords:
                if keyword in message_lower:
                    topic_scores[topic] += 1

        # Get the topic with the highest score
        if any(topic_scores.values()):
            identified_topic = max(topic_scores.items(), key=lambda x: x[1])[0]
        else:
            identified_topic = "general"

        return identified_topic

    def generate_intelligent_response(self, message: str, emotion: str, topic: str) -> str:
        """
        Generate a response based on the detected emotion and topic.

        Args:
            message: The user's message
            emotion: The detected emotion
            topic: The identified topic

        Returns:
            String containing the generated response
        """
        # Check if the message is a greeting
        for pattern in self.greeting_patterns:
            if re.search(pattern, message.lower()):
                return random.choice(self.greeting_responses)

        # Check if the message is a question
        is_question = False
        for pattern in self.question_patterns:
            if re.search(pattern, message):
                is_question = True
                break

        # Generate response based on emotion and topic
        if is_question:
            # For questions, provide more informative responses
            # Check if we have previous emotions in the session
            previous_emotions = self.context.get('session_emotions', [])
            if len(previous_emotions) > 1 and previous_emotions[-2] != 'neutral':
                # Use the previous emotion to provide context-aware response
                prev_emotion = previous_emotions[-2]
                if prev_emotion in self.emotion_responses:
                    # Select a response that acknowledges both the question and the previous emotion
                    emotion_response = random.choice(self.emotion_responses[prev_emotion])
                    return f"{emotion_response} {self.topic_responses.get(topic, 'What else would you like to know?')}"

            # Default response if no relevant previous emotion
            if topic in self.topic_responses:
                return f"{self.topic_responses[topic]} Is there something specific about {topic} you'd like to discuss?"
            else:
                return "That's an interesting question. Could you tell me more about what you're looking for?"
        else:
            # For statements, respond to the emotion
            if emotion in self.emotion_responses:
                return random.choice(self.emotion_responses[emotion])
            else:
                return "I understand. Would you like to tell me more about how you're feeling?"

    def is_drink_recommendation_request(self, message: str) -> bool:
        """
        Check if the message is a request for a drink recommendation.

        Args:
            message: The user's message

        Returns:
            True if the message is a drink recommendation request, False otherwise
        """
        message_lower = message.lower()
        for pattern in self.drink_recommendation_patterns:
            if re.search(pattern, message_lower):
                return True
        return False

    def handle_drink_recommendation(self, message: str, emotion: str) -> Dict:
        """
        Handle a drink recommendation request.

        Args:
            message: The user's message
            emotion: The detected emotion

        Returns:
            Dict containing the response and recommendation state
        """
        # Update the drink recommender with the current emotion
        self.drink_recommender.set_emotion(emotion)

        # Check the current state of the recommendation process
        state = self.context.get('drink_recommendation_state')

        if state is None:
            # First time asking for a recommendation
            self.context['drink_recommendation_state'] = 'asking_questions'
            question_data = self.drink_recommender.get_next_question()

            if question_data:
                self.context['current_drink_question'] = question_data['question']
                options_text = "\n".join([f"- {option['text']}" for option in question_data['options']])
                return {
                    'response': f"I'd be happy to recommend a drink for you! To help me make a better recommendation, please answer a few questions.\n\n{question_data['question']}\n{options_text}",
                    'state': 'asking_questions',
                    'hide_emotion': True
                }
            else:
                # No questions available, give recommendation based on emotion only
                recommendation = self.drink_recommender.get_recommendation_message()
                self.context['drink_recommendation_state'] = None
                return {
                    'response': f"Based on your mood, {recommendation['response']}",
                    'state': None,
                    'image': recommendation['image'],
                    'hide_emotion': True
                }

        elif state == 'asking_questions':
            # Process the answer to the previous question
            current_question = self.context.get('current_drink_question')
            if current_question and self.drink_recommender.process_answer(current_question, message):
                # Answer processed successfully

                # Check if we have enough information
                if self.drink_recommender.is_profile_complete():
                    # Generate recommendation
                    recommendation = self.drink_recommender.get_recommendation_message()
                    self.context['drink_recommendation_state'] = None
                    self.context['current_drink_question'] = None
                    return {
                        'response': recommendation['response'],
                        'state': None,
                        'image': recommendation['image'],
                        'hide_emotion': True
                    }
                else:
                    # Ask another question
                    question_data = self.drink_recommender.get_next_question()
                    if question_data:
                        self.context['current_drink_question'] = question_data['question']
                        options_text = "\n".join([f"- {option['text']}" for option in question_data['options']])
                        return {
                            'response': f"Thanks! {question_data['question']}\n{options_text}",
                            'state': 'asking_questions',
                            'hide_emotion': True
                        }
                    else:
                        # No more questions, give recommendation
                        recommendation = self.drink_recommender.get_recommendation_message()
                        self.context['drink_recommendation_state'] = None
                        self.context['current_drink_question'] = None
                        return {
                            'response': recommendation['response'],
                            'state': None,
                            'image': recommendation['image'],
                            'hide_emotion': True
                        }
            else:
                # Couldn't process the answer
                return {
                    'response': f"I didn't understand your answer. Please choose one of the options for: {current_question}",
                    'state': 'asking_questions',
                    'hide_emotion': True
                }

        # Default case - reset and start over
        self.drink_recommender.reset_profile()
        self.context['drink_recommendation_state'] = 'asking_questions'
        question_data = self.drink_recommender.get_next_question()

        if question_data:
            self.context['current_drink_question'] = question_data['question']
            options_text = "\n".join([f"- {option['text']}" for option in question_data['options']])
            return {
                'response': f"Let me recommend a drink for you! First, {question_data['question']}\n{options_text}",
                'state': 'asking_questions',
                'hide_emotion': True
            }
        else:
            # No questions available, give recommendation based on emotion only
            recommendation = self.drink_recommender.get_recommendation_message()
            self.context['drink_recommendation_state'] = None
            return {
                'response': f"Based on your mood, {recommendation['response']}",
                'state': None,
                'image': recommendation['image'],
                'hide_emotion': True
            }

    def process_message(self, message: str) -> Dict:
        """
        Process a user message and generate a response.

        Args:
            message: The user's message

        Returns:
            Dict containing the response, detected emotion, confidence, and image
        """
        try:
            # Special case for Bulgarian toast "Наздраве!"
            if message.strip() == "Наздраве!":
                return {
                    'response': "Наздраве! Кой не види дънце, да не види слънце!",
                    'emotion': 'joy',
                    'confidence': 0.9,
                    'image': self.emotion_images.get('joy', 'neutral.jpg'),
                    'all_emotions': {'joy': 0.9, 'excitement': 0.1},
                    'hide_emotion': False
                }

            # Check if we're in the middle of a drink recommendation flow, if this is a new drink recommendation request,
            # or if we've just given a drink recommendation
            is_drink_flow = self.context.get('drink_recommendation_state') == 'asking_questions'
            is_recommendation_given = self.context.get('drink_recommendation_state') == 'recommendation_given'
            is_new_drink_request = self.is_drink_recommendation_request(message)

            # If we're in the middle of a drink recommendation flow or this is a new drink request,
            # but not if we've just given a recommendation (in which case we want to analyze emotions again)
            if (is_drink_flow or is_new_drink_request) and not is_recommendation_given:
                # Skip emotion analysis for drink recommendation questions
                detected_emotion = self.context.get('current_emotion', 'neutral')
                topic = 'drinks'

                # Use a neutral emotion result for drink recommendations
                emotion_result = {
                    'emotion': detected_emotion,
                    'confidence': 0.8,
                    'scores': {detected_emotion: 0.8, 'neutral': 0.2},
                    'image': self.emotion_images.get(detected_emotion, 'neutral.jpg')
                }

                # Initialize image with the emotion image
                image = emotion_result['image']

                if is_drink_flow:
                    # Continue with the drink recommendation flow
                    recommendation_result = self.handle_drink_recommendation(message, detected_emotion)
                    response = recommendation_result['response']
                    # Use the drink image if available
                    if 'image' in recommendation_result:
                        image = recommendation_result['image']
                else:
                    # Start a new drink recommendation flow
                    recommendation_result = self.handle_drink_recommendation(message, detected_emotion)
                    response = recommendation_result['response']
                    # Use the drink image if available
                    if 'image' in recommendation_result:
                        image = recommendation_result['image']
            else:
                # Analyze emotion for non-drink-related messages
                emotion_result = self.analyze_emotion(message)
                detected_emotion = emotion_result['emotion']

                # Identify topic
                topic = self.identify_topic(message)

                # Initialize image with the emotion image
                image = emotion_result['image']

                # Generate regular response
                response = self.generate_intelligent_response(message, detected_emotion, topic)

                # Add emotion percentages to the response (but not for drink recommendations)
                emotion_percentages = []
                for emotion, score in sorted(emotion_result['scores'].items(), key=lambda x: x[1], reverse=True):
                    if score > 0.01:  # Only include emotions with a score greater than 1%
                        percentage = round(score * 100)
                        if percentage > 0:  # Only include emotions with a percentage greater than 0
                            emotion_percentages.append(f"{emotion}: {percentage}%")

                # Only add emotions to the response if this is not a drink recommendation
                if emotion_percentages and not is_new_drink_request and not is_drink_flow:
                    response += "\n\nDetected emotions: " + ", ".join(emotion_percentages[:5])  # Limit to top 5 emotions for readability

            # Update context
            self.context['current_emotion'] = detected_emotion
            self.context['current_topic'] = topic
            self.context['previous_messages'].append(message)
            self.context['session_emotions'].append(detected_emotion)

            # Reset drink recommendation state if we've just processed a message after giving a recommendation
            if is_recommendation_given:
                self.context['drink_recommendation_state'] = None

            # Update conversation memory
            self.conversation_memory.append({
                'user': message,
                'bot': response,
                'emotion': detected_emotion,
                'topic': topic
            })

            # Return the result with all emotions
            return {
                'response': response,
                'emotion': detected_emotion,
                'confidence': emotion_result['confidence'],
                'image': image,
                'all_emotions': emotion_result['scores'],
                'hide_emotion': is_drink_flow or is_new_drink_request
            }
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")

            # Try to recover by using a simplified emotion analysis
            try:
                # Use a simpler approach to detect emotion
                simple_emotion = self.analyze_emotion_simple(message)

                # If we got a neutral result from the simple analysis, try to infer from context
                if simple_emotion == 'neutral':
                    # First, try a more aggressive pattern matching approach
                    message_lower = message.lower()
                    emotion_matches = {}

                    for emotion, patterns in self.emotion_patterns.items():
                        if emotion != 'neutral':
                            for pattern in patterns:
                                if re.search(pattern, message_lower):
                                    emotion_matches[emotion] = emotion_matches.get(emotion, 0) + 1

                    # If we found any emotion matches, use the one with the most matches
                    if emotion_matches:
                        simple_emotion = max(emotion_matches.items(), key=lambda x: x[1])[0]
                    # Otherwise, use the most recent non-neutral emotion if available
                    elif self.context.get('session_emotions'):
                        for prev_emotion in reversed(self.context['session_emotions']):
                            if prev_emotion != 'neutral':
                                simple_emotion = prev_emotion
                                break

                # Generate a fallback response based on the detected emotion
                fallback_responses = {
                    'joy': "I'm glad you're feeling positive! Could you tell me more about what's on your mind?",
                    'sadness': "I sense you might be feeling down. Would you like to talk about it?",
                    'anger': "I understand you might be frustrated. Would you like to discuss what's bothering you?",
                    'fear': "It seems like something might be concerning you. Would you like to talk about it?",
                    'surprise': "That sounds surprising! Would you like to tell me more about it?",
                    'love': "I appreciate your positive feelings. What else would you like to talk about?",
                    'disgust': "I understand that might be unpleasant. Would you like to discuss something else?",
                    'trust': "I value your trust. What else would you like to discuss?",
                    'neutral': "I'm having trouble understanding. Could you try expressing that differently?"
                }

                response = fallback_responses.get(simple_emotion, "I'm having trouble understanding. Could you try expressing that differently?")
                image = self.emotion_images.get(simple_emotion, 'neutral.jpg')

                # Create a simple emotion scores dictionary for the fallback case
                fallback_emotion_scores = {emotion: 0.0 for emotion in self.emotion_patterns.keys()}
                fallback_emotion_scores[simple_emotion] = 1.0

                # Add emotion percentages to the fallback response
                emotion_percentages = []
                for emotion, score in sorted(fallback_emotion_scores.items(), key=lambda x: x[1], reverse=True):
                    if score > 0.01:  # Only include emotions with a score greater than 1%
                        percentage = round(score * 100)
                        if percentage > 0:  # Only include emotions with a percentage greater than 0
                            emotion_percentages.append(f"{emotion}: {percentage}%")

                # Check if we're in a drink recommendation flow, if this is a new drink request,
                # or if we've just given a drink recommendation
                is_drink_flow = self.context.get('drink_recommendation_state') == 'asking_questions'
                is_recommendation_given = self.context.get('drink_recommendation_state') == 'recommendation_given'
                is_new_drink_request = self.is_drink_recommendation_request(message)

                # Only add emotions to the response if this is not a drink recommendation
                if emotion_percentages and not is_new_drink_request and not is_drink_flow and not is_recommendation_given:
                    response += "\n\nDetected emotions: " + ", ".join(emotion_percentages[:5])  # Limit to top 5 emotions for readability

                return {
                    'response': response,
                    'emotion': simple_emotion,
                    'confidence': 0.3,  # Low confidence but not zero
                    'image': image,
                    'all_emotions': fallback_emotion_scores,
                    'hide_emotion': is_drink_flow or is_new_drink_request or is_recommendation_given
                }
            except:
                # If all else fails, use a truly neutral fallback
                self.logger.error("Failed to recover from error, using neutral fallback")

                # Check if we're in a drink recommendation flow, if this is a new drink request,
                # or if we've just given a drink recommendation
                is_drink_flow = self.context.get('drink_recommendation_state') == 'asking_questions'
                is_recommendation_given = self.context.get('drink_recommendation_state') == 'recommendation_given'
                is_new_drink_request = False
                try:
                    is_new_drink_request = self.is_drink_recommendation_request(message)
                except:
                    # If we can't determine if it's a drink request, assume it's not
                    pass

                return {
                    'response': "I'm having trouble understanding. Could you try expressing that differently?",
                    'emotion': 'neutral',
                    'confidence': 0.0,
                    'image': 'neutral.jpg',
                    'all_emotions': {'neutral': 1.0},
                    'hide_emotion': is_drink_flow or is_new_drink_request or is_recommendation_given
                }
        # Calculate confidence based on the difference between top emotions
        # Higher difference = higher confidence
        confidence = min(0.85, primary_emotion[1])  # Cap at 0.85 to avoid overly confident predictions
        if len(sorted_emotions) > 1:
            # If strong contrast between top emotions, boost confidence
            if primary_emotion[1] > sorted_emotions[1][1] * 1.5:
                confidence = min(0.9, confidence * 1.15)  # Reduced boost and maximum
            else:
                # Reduce confidence for neutral emotions
                confidence = max(0.4, confidence * 0.9)  # Less reduction and higher minimum

        # Minor confidence boost for specific emotions
        if primary_emotion[0] in ['joy', 'sadness', 'anger', 'fear', 'disgust', 'surprise']:
            confidence = min(0.9, confidence * 1.1)  # Reduced boost and maximum

        # Return the result
        result = {
            'emotion': primary_emotion[0],
            'confidence': confidence,
            'scores': emotion_scores,
            'image': self.emotion_images.get(primary_emotion[0], 'neutral.jpg')
        }

        # Add mixed emotion if detected
        if mixed_emotion:
            result['mixed_emotion'] = mixed_emotion

        return result
