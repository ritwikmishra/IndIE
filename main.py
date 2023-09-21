# -*- coding: utf-8 -*-
# export CUDA_DEVICE_ORDER=PCI_BUS_ID; export TOKENIZERS_PARALLELISM=false
# CUDA_VISIBLE_DEVICES=0 python main.py

from chunking.chunking_model import *
from chunking.crf_chunker import *
from utils import *
import pandas as pd
from tqdm import tqdm
import stanza, torch

use_gpu = torch.cuda.is_available() 

# loading all the languages here
hindi_nlp = load_stanza_model(lang='hi', use_gpu=use_gpu)
tamil_nlp = load_stanza_model(lang='ta', use_gpu=use_gpu)
telugu_nlp = load_stanza_model(lang='te', use_gpu=use_gpu)
urdu_nlp = load_stanza_model(lang='ur', use_gpu=use_gpu)

nlp = hindi_nlp

hyper_params = {
	'run_ID': 26,
	'createData': True,
	'bs': 8,
	'bert_model_name': 'xlm-roberta-base',
	'available_models': "'ai4bharat/indic-bert' 'bert-base-multilingual-cased' 'xlm-roberta-base' 'bert-base-multilingual-uncased' 'xlm-mlm-100-1280' 'xlm-mlm-tlm-xnli15-1024' 'xlm-mlm-xnli15-1024'",
	'alpha' : 0.00001,
	'epochs': 3,
	'rseed': 123,
	'nw': 4,
	'train_ratio' :  0.7,
	'val_ratio' : 0.1,
	'max_len' : 275,
	'which_way' : 3,
	'which_way_gloss': "1= take first wordpiece token id | 2= take last wordpiece token id | 3= average out the wordpiece embeddings during the forward pass",
	'embedding_way' : 'last_hidden_state',
	'embedding_way_gloss': 'last_hidden_state, first_two, last_two',
	'notation' : 'BI',
	'platform': 1,
	'available_platforms': "MIDAS server = 1, colab = 2",
	'chunker':'XLM' # CRF or XLM
}

model_embeddings = {
	'ai4bharat/indic-bert':768,
	'bert-base-multilingual-cased':768,
	'xlm-roberta-base':768,
	'bert-base-multilingual-uncased':768,
	'xlm-mlm-100-1280':1280,
	'xlm-mlm-tlm-xnli15-1024':1024,
	'xlm-mlm-xnli15-1024':1024
}

hyper_params['embedding_size'] = model_embeddings[hyper_params['bert_model_name']]

my_tagset = torch.load('chunking/data/my_tagset_'+hyper_params['notation']+'.bin')

hyper_params['my_tagset'] = my_tagset

os.environ['PYTHONHASHSEED'] = str(hyper_params['rseed'])
# Torch RNG
torch.manual_seed(hyper_params['rseed'])
torch.cuda.manual_seed(hyper_params['rseed'])
torch.cuda.manual_seed_all(hyper_params['rseed'])
# Python RNG
np.random.seed(hyper_params['rseed'])
random.seed(hyper_params['rseed'])

is_cuda = torch.cuda.is_available()

if is_cuda and use_gpu:
	device = torch.device("cuda:0")
	t = torch.cuda.get_device_properties(device).total_memory
	c = torch.cuda.memory_reserved(device)
	a = torch.cuda.memory_allocated(device)
	f = t -(c-a)  # free inside cache
	print("GPU is available", torch.cuda.get_device_name(), round(t/(1024*1024*1024)), "GB")
else:
	device = torch.device("cpu")
	print("GPU not available, CPU used")

hyper_params['device'] = str(device)

if hyper_params['chunker'] == 'XLM':
	print('Creating the XLM chunker model...')
	model = chunker_class(device, hyper_params).to(device)
	checkpoint = torch.load('chunking/state_dicts/model/'+str(hyper_params['run_ID'])+'_epoch_4.pth.tar',map_location=device)
	print(model.load_state_dict(checkpoint['state_dict']))
	tokenizer = AutoTokenizer.from_pretrained(hyper_params['bert_model_name'])
elif hyper_params['chunker'] == 'CRF':
	model, tokenizer = 'CRF', 'CRF'


# -------------- This is for single extraction --------------
ml = ["पिछले वर्ष शुरू की गई इस योजना के तहत भारत सरकार की ओर से बच्चे और उसके एक अभिभावक का विमान किराया और रहने का खर्चा मुहैया कराया जाता है ।","भारतीय जनता पार्टी के पूर्व महासचिव और संगठन मंत्री संजय जोशी के आपत्तिजनक और विवादस्पद सीडी के मामले से राष्ट्रीय महिला आयोग ने अपना पल्ला झाड़ लिया है ।","वार्ता में कश्मीर मुद्दे को शामिल किए जाने के बारे में रूस की यात्रा पर गए विदेश सचिव शशांक ने बताया है ।","लेकिन कांग्रेस से किसी ने भी उन्हें बधाई नहीं दी ।","शादी के वक्त चार गवाहों की मौजूदगी में दोनों पक्षों को इस करार पर दस्तखत करने होंगे ।","प्रधानमंत्री के मीडिया सलाहकार संजय बारू ने बैठक के बाद संवादाताओं को बताया कि प्रधानमंत्री इस वार्ता प्रक्रिया में सभी पुरुषों और महिलाओं की सहमति चाहते हैं जिससे लोगों की पीड़ा दूर हो सके ।","इस हादसे में घायल एक व्यक्ति ने बताया कि विस्फोट के बाद घटनास्थल पर मानव अंग बिखरे पड़े थे और पूरे प्लेटफॉर्म पर खून के छींटे नजर आ रहे थे ।","इस कार्य की शुरुआत उन्होंने अपने बिजनेसमैन दोस्त के लिए की थी ।","उन्हें सत्र न्यायालय के पिछले दरवाजे से दर्जनों समर्थकों के घेरे में चुपके से अदालत में पेश किया गया.","मामले के संबंध में पुलिस अधीक्षक रणबीर शर्मा का कहना है कि मामले की जाँच के आदेश थाना सदर प्रभारी को दे दिये गए हैं तथा जाँच के बाद ही कोई कार्रवाई की जाएगी ।","दूसरी ओर आज कुछ खबरों में कहा गया है कि रिलायंस एनर्जी के अध्यक्ष एवं प्रबंध निदेशक अनिल अंबानी ने विभिन्न विद्युत परियोजनाओं में १४००० करोड़ रुपये के निवेश के बारे में रिलायंस इंडस्ट्रीज को पिछले वित्तीय वर्ष में सूचित किया था ।","इस पर यात्रियों ने जोर - जोर से चिल्लाना शुरू कर दिया ।","पर उन्होंने यह कहते हुए इनकार कर दिया कि केवल एक स्टीकर जारी किया जाता है ।","उसके दाहिने कूल्हे के बदले जाने को लंबी बीमारी से जोड़कर देखना उचित नहीं है ।","दलाई लामा ने कहा कि मैं तिब्बती समस्या का सार्थक और मान्य हल ढूंढ़ने की कोशिश में हूं ।","सीईसीए १ अगस्त से लागू हो जाएगा ।","अपने चचेरे भाई और शिवसेना के कार्यकारी अध्यक्ष उद्धव ठाकरे से खफा राज ठाकरे ने शिवसेना सुप्रीमो बाल ठाकरे को कड़ा लिखा और पूछा कि मालवण की हार के लिए जिम्मेदार कौन है?","सूत्रों के मुताबिक इस बैठक से ठीक पहले मुकेश ने अनिल व १२ निदेशकों के साथ अलग से बैठक की थी ।","लेकिन, इसमें थलसेना की भागीदारी अपने आप में महत्वपूर्ण है ।","उन्होंने कहा कि यह सभी लोगों को महसूस करना होगा कि बिहार में लालू प्रसाद की पार्टी सबसे बड़ा धर्मनिरपेक्ष दल है ।","रामविलास पासवान पर हमला करके वह कांग्रेस पर दबाव डाल रहे थे कि वह पासवान को लाइन पर लाए ।","बुधवार को रक्षा मंत्री प्रणव मुखर्जी ने नवंबर में जम्मू कश्मीर में घुसपैठ में इजाफे की बात कही ।","जेसिका लाल, मेहर भार्गव और भाजपा नेता प्रमोद महाजन के बीच क्या समानता है ।","उन्होंने मुख्यमंत्री मुलायम सिंह के आवास पर एक संवाददाता सम्मेलन को भी सम्बोधित किया ।","उन्होंने कहा कि पर्वतारोहण एवं खेल निदेशालय के उदासीन रवैये के कारण आज अन्य युवा खिलाड़ियों को उनकी प्रतिभा दिखाने का मौका नहीं मिल रहा है ।","यमनोत्री के पट हर साल हिन्दू कैलेंडर के अनुसार अक्षय तृतीया के दिन खोले जाते हैं.","लालू यादव ने इसके लिए जिसका नाम भेजा उसे नियुक्ति संबंधी कैबिनेट की समिति ने नामंजूर कर दिया ।","क्योंकि, जिन्हें भी थलसेना की कार्यप्रणाली और युद्ध के दिनों में की जाने वाली तैयारी के बारे में जानकारी है, वे इस तरह की बात नहीं कह सकते कि थलसेना समय पर तैयार नहीं थी ।","दरअसल जेल आज अपराध के अड्डे बनते जा रहे हैं ।","फतुहा अस्पताल के चिकित्सा अधिकारी आर. एन. पी. सिन्हा ने बताया कि २५ घायलों को पटना के नालंदा मेडिकल कॉलेज व हॉस्पिटल में भेज दिया गया है ।","सांख्यिकी मंत्रालय के मुताबिक ४४ बिजली परियोजनाएं जिन पर काम चल रहा है ।","गुप्त सूचना पर पुलिस पहुंची और छापा मारकर मिस्टर एक्स व अन्य को दबोच लिया और गैंबलिंग एक्ट १८६७ की धारा १३ के तहत केस दर्ज कर उन्हें हवालात में बंद कर दिया.","यह प्रतिबंध एक जुलाई, २००७ से लागू होगा ।","पैत्रोदा ने मंगलवार शाम 'भारतीय विज्ञान २१वीं शताब्दी में' विषय पर अपने विचार रखते हुए वृहद सीएसआईआर के पूर्ण विकेंद्रीकरण की मांग कर डाली ।","कहा गया कि दोनों भाईयों में मनमुटाव भी इसी वजह से हुआ ।","अब उसने अपनी बहन को भी बुला लिया है ।","पुलिस सूत्रों के अनुसार फिलहाल किसी के हताहत होने अथवा संपत्ति के नुकसान की सूचना नहीं मिली है, लेकिन काफी संख्या में पेड़ उखड़ गए हैं ।","पूर्वी सीमा पर अवैध घुसपैठ की समस्या के समाधान के लिए भारत ने शुक्रवार को बांग्लादेश से 'एक उपयुक्त व्यवस्था या प्रोटोकॉल' स्थापित करने को कहा है.","इस पार्टी की छवि महिलाओं के हक के लिए लड़ने वाली पार्टी के तौर पर हो ।","इसके अलावा ११ लोग लापता बताए गए थे ।","फर्नाँडिस ने शनिवार को कहा कि इस मामले में उन्हें क्लीन चिट मिल चुकी है ।","पार्टी का कहना है कि दोनों दलों के बीच स्वस्थ मतभेद है ।","हालांकि इस बार सात नए मामले आये हैं इससे केन्द्र सरकार संतुष्ट नहीं है ।","इस अभियान के दौरान इस आतंकी संगठन को अपने १० वरिष्ठ कमांडरों से हाथ धोना पड़ा ।","अमेरिकी अधिकारियों ने इन टेपों की विश्वसनीयता की पुष्टि की है ।","सभी के लिए समान कानून का जिक्र करते हुए तेलगुदेशम पार्टी के प्रमुख चंद्रबाबू नायडू ने रैली में कहा कि हम सोनिया पर हमला नहीं कर रहे हैं ।","गौरतलब है कि लंदन में जी - ४ के देशों के साथ हुई बैठक में अफ्रीकी संघ ने जी - ४ के साथ संयुक्त प्रस्ताव पेश करने पर सहमति व्यक्त की थी, लेकिन इथियोपिया की राजधानी आदिस अबाबा में हुई अफ्रीकी संघ की शिखर बैठक में संयुक्त प्रस्ताव पेश करने के विचार को सिरे से ही ठुकरा दिया गया ।","उन्हें जनता की सेवा के लिए भी आवश्यक संसाधन उपलब्ध नहीं हैं ।","ग्रामीणों में रोष है कि पुलिस इस मामले में केस दर्ज करने में आनाकानी कर रही है ।","दुलइमी संकट को लंबा खींचने के लिए कुवैत एंड गल्फ लिंक (केजीएल) कंपनी को भी दोषी मानते हैं, जिसके लिए ये ड्राइवर काम करते थे ।","दसवीं की परीक्षा में कुल दो लाख ९८ हजार २६ विद्यार्थी शामिल हुए थे ।","रविवार को 'दी मेल' ने एफबीआई के हवाले से लिखा कि 7 जुलाई को लंदन में हुए धमाकों के पीछे असवत का ही हाथ है, लेकिन उच्च पदस्थ ब्रिटिश सुरक्षा सूत्रों ने हमले में असवत के शामिल होने की बात से इनकार किया है ।","कई बार तो विभाग के कर्मचारी ही उन्हें निजी डाक्टर के यहां भेज देते हैं ।","करीब 23 अमेरिकी विश्वविद्यालयों ने भारत के 39 कृषि विश्वविद्यालयों और कृषि संस्थानों के साथ सहयोग की इच्छा जताई है ।","आगामी चुनाव में ज्यादा सीट जीतकर लालू - राबड़ी को मात देने के लिए कार्य योजनाओं पर चर्चा हुई ।","उन्होंने कहा कि रेंटल व्यापार के लिए अब तक इन कारों का उपयोग नहीं किया है ।","मनमोहन सिंह ने इस संबंध में राज्यों से अपनी प्रतिबद्घताओं को पूरा करने की अपील की है ।","महाजन ने कहा कि इस बार चुनाव का मुख्य मुद्दा विकास होगा ।","प्रधानमंत्री मनमोहन सिंह रविवार को मलेशिया के चार दिनी दौरे पर रवाना होंगे ।","तीन भारतीय सहित सात ट्रक ड्राइवरों की रिहाई के लिए मध्यस्थ की भूमिका निभा रहे शेख दुलइमी ने कहा है कि अगर भारतीय फिल्मी सितारे खासकर अमिताभ, धर्मेंद्र व आशा पारिख बंधकों को आजाद करने की टेलीविजन पर अपील करें तो उन्हें तत्काल रिहा कर दिया जाएगा ।","देश में एनसीपी की अपनी अलग पहचान है ।","वन विभाग में भी रेंजर से लेकर ऊपर तक के अफसरों के घरों में फारेस्ट वर्कर के नाम पर तैनात दिहाड़ीदार साहबों की खिदमत में हैं ।","अतरजीत इसमें शामिल था ।","यूपीए सरकार न्यूनतम साझा कार्यक्रम (सीएमपी) में भी ऐसा वादा कर चुकी है ।","करेहड़ा के तीन बच्चे अंकुर, संदीप व प्रशांत यमुना नदी में बाढ़ का पानी देखने के लिए गांव लाल छप्पर की ओर जा रहे थे कि सड़क पर अधिक पानी होने की वजह से डूबने लगे ।","इराकी विद्रोहियों की शरणस्थली फालुजा में तेज अमेरिकी हमले की निंदा करते हुए बगदाद यूनिवर्सिटी में इंटरनेशनल स्टडीज के प्रोफेसर नबील मोहम्मद ने कहा कि यह उचित नहीं है कि होने वाले चुनाव को लोकतांत्रिक करार दिया जाए ।","जहां तक आरआईएल का सवाल है अंबानी परिवार के लिए यह भावनात्मक मुद्दा है और अभी तक यह स्पष्ट नहीं है कि मुकेश और अनिल में से कौन आरआईएल पर काबिज होगा ।","मौसम विभाग के अनुसार दिल्ली में रविवार सुबह से जारी रिमझिम बारिश मानसून पूर्व बारिश है ।","दोनों सदनों में जम्मू - कश्मीर और पाकिस्तान में आए विनाशकारी भूकंप, दिवाली से पहले दिल्ली में हुए विस्फोटों, आंध्र प्रदेश की रेल दुर्घटना और जार्डन की हाल की आतंकी घटना समेत इन सभी हादसों में मारे गए व घायल हुए लोगों के प्रति संवेदना व्यक्त करते हुए बम धमाकों व आतंकी हमलों की निंदा की गई ।","वोहरा ने मंगलवार को प्रधानमंत्री मनमोहन सिंह से मुलाकात कर उन्हें हुर्रियत कांफ्रेंस समेत राज्य के विभिन्न अलगाववादी समूहों से बातचीत की जानकारी दी ।","वीरता पदक पाने के लिए देश के पूर्वोत्तर हिस्से में घुसपैठियों से फर्जी मुठभेड़ की फिल्म बनाने के मामले में शुक्रवार को उस समय नया मोड़ आ गया जब अनुशासनात्मक मामलों में ब्रिगेडियर की खिंचाई की गई ।","दूसरी ओर आरएसपी और फॉरवर्ड ब्लॉक का मानना है कि कांग्रेस सोनिया गांधी के इस्तीफे को भुनाने में कोई कोर - कसर नहीं छोड़ेगी ।","संघ प्रमुख ने एक बार फिर दोहराया कि संघ के संगठन अनेक हैं किंतु विचारधारा एक ही है ।","सोमवार को दिल्ली जाने के कारण के बारे में पूछे जाने पर उन्होंने कहा कि इसके पीछे कोई कारण नहीं है ।","इसमें उत्तर प्रदेश भी शामिल है जहां से सिर्फ १५ जिले इस कार्यक्रम में शामिल हैं ।","उससे पूछताछ की जा रही है ।","उन्होंने ऋण वितरण को प्रोत्साहित करने के लिए ऋण का 10 फीसदी रिस्क फंड के रूप में उपलब्ध कराने पर भी बल दिया ।","द्विपक्षीय बातचीत के लिए किसी भारतीय विदेश मंत्री की १७ साल में यह पहली पाकिस्तान यात्रा होगी ।","विदित हो कि कर्नाटक में आगामी अक्तूबर में जद (एस) भाजपा को मुख्यमंत्री की कुर्सी सौंपेगी.","बिहार के राज्यपाल बूटा सिंह ने बृहस्पतिवार को मुजफ्फरपुर जिले के बाढ़ प्रभावित इलाकों में अनुपस्थित चिकित्सकों को तुरंत निलंबित करने के आदेश दिए हैं और जिलाधिकारी को बिना चिकित्सक वाले स्वास्थ्य केंद्रों में निजी चिकित्सकों को नियुक्त करने को कहा है ।","अधिकतम तापमान ३७ डिग्री सेल्सियस रहने का अनुमान है ।","यह मामला ऐसे वक्त उठा है, जब बाल ठाकरे मालवन में हार के मद्देनजर पार्टी संगठन को दुरुस्त करने की सोच रहे थे ।","सिन्हा ने कहा कि जिस तरह भारत सरकार ने हुर्रियत नेताओं को बिना पासपोर्ट पाकिस्तान जाने की अनुमति दी वह गलत था ।","उन्होंने कहा कि हमने इन हमलों के जिम्मेदार लोगों का पता लगाने के लिए भारत और पाक सरकार से मदद मांगी है ।","उन्होंने वैसे मामलों का उदाहरण दिया, जहां ऐसे कानूनों के क्रियान्वयन से लोगों को खासकर मुस्लिम युवतियों को प्रताड़ित किया गया ।","मार्च महीने में जब भारत और पाकिस्तान के विदेश मंत्री इस्लामाबाद में बैठेंगे तो क्या सियाचिन से सेना हटाने पर सहमति बन जाएगी?","जज ने हत्या के इरादे पर प्रकाश डालते हुए कहा कि अभियोजन पक्ष के मुताबिक शंकराचार्य किसी भी कीमत पर शंकररमन को रास्ते से हटाना चाहते थे ।","एक हफ्ते में एफआईआई ने १३६४.५० करोड़ रुपये की लिवाली की है ।","वह इससे ऊपर नहीं है ।","पर्यटकों की खासी आवाजाही ने इस उपनगर को महानगर जैसा रूप दे दिया है ।","उन्होंने कहा कि अध्यादेश में लाभ के पद की सूची से कुछ पदों को हटा दिया जाएगा ताकि कुछ सांसदों की सदस्यता बची रहे ।","भट्ट ज्योतिषी परिवार से संबंधित हैं और खुद विज्ञान के छात्र रहे हैं ।","नगर के शाही कटरा के मैदान में बृहस्पतिवार को भरत मिलाप के आयोजन के लिए बज रहे लाउडस्पीकर को समुदाय विशेष के कुछ लोगों द्वारा जबरिया बंद कराए जाने के विरोध में शुक्रवार की सुबह हिंसा भड़क उठी ।","उस मिलन की कल्पना कर वे रोमांचित हो उठती हैं ।","इससे पहले अय्यर ने वित्त मंत्री पी. चिदंबरम के साथ प्रधानमंत्री मनमोहन सिंह से इस मसले पर चर्चा की और विभिन्न विकल्पों पर विचार किया ।","असम के मुख्यमंत्री तरुण गोगोई ने शनिवार को यहाँ पत्रकारों से कहा कि उनकी सरकार वार्ता के लिए प्रधानमंत्री कार्यालय की ओर से हाल में दिए निमंत्रण पर फैसला करने के लिए उल्फा की केंद्रीय कार्यकारिणी बैठक में शामिल होने के लिए सदस्यों को रिहा करने को तैयार है ।","करीब १.१५ बजे पुलिस ने जबरदस्ती जाम खुलवा दिया ।","पहले चरण के चुनाव में राजद 64 में से 58 सीटों पर चुनाव लड़ रही है और उसने तीन सीटे भाकपा, दो सीटें माकपा और एक सीट कांग्रेस पार्टी के लिए छोड़ी है ।","महीने भर चले ड्रामे के बाद पार्टी ने उनका निलंबन रद्द कर दिया है पर भाजपा महासचिव के रूप में उनकी बहाली पर पार्टी ने साफ कुछ नहीं कहा है ।","आतंकियों ने तेज धारदार हथियारों से उनके गले रेत दिए ।","इस मामले की सुनवाई बंद कमरे में कराने के लिए उन्होंने पहले निचली अदालत और अब हाईकोर्ट में याचिका दायर की है ।","जैम्स को एक होटल से अगवा कर लिया गया था ।","क्योंकि, गन्ने के सीजन के शुरू होते ही इन उत्पादकों ने किसानों को 125 रुपये से लेकर 130 रुपए प्रति कुंतल की कीमत देनी शुरू कर दी ।","दूसरी पारी में पाक बल्लेबाजों ने जिम्मेदारी का परिचय दिया और मैच को लगभग अपनी पकड़ में कर लिया ।","पूरे कार्यक्रम की फिल्म भी बनी है जिसमें स्विच आफ किए जाने की बात साफ हो गई है ।","पुलिस ने मामला दर्ज कर जांच शुरू कर दी है ।","सुब्रमण्यन ने कहा कि पप्पू यादव के मामले में सुप्रीम कोर्ट के आदेश को इस मामले में लागू नहीं किया जा सकता ।","बोर्ड ने कोई विरोध क्यों नहीं किया ।"]
# ml = ["आदिम युग में सब लोग दिन भर काम से थक जाने के बाद मनोरंजन के लिए कही खुले में एक घेरा बनाकर बैठ जाते थे और उस घेरे के बीचों-बीच ही उनका भोजन पकता रहता , खान-पान होता और वही बाद में नाचना-गाना होता ।"]
ml = ['Abdus Salam, a Pakistani scientist, was a good person.']
ml = ['शर्मीला टैगोर के बेटे सैफ अली खान को 2010 में पद्मा श्री पुरस्कार मिला। वह एक भारतीय अभिनेता है।']
# ml = ['शाह रुख खान गौरी खान के पति है।']

# _, ml = resolve_coreferences_for_hindi(ml, coref_model, nlp)

start_time = time.time()
for s in tqdm(ml,total=len(ml)):
	all_sents, exts, ctime, etime = perform_extraction(s,lang,model,tokenizer, nlp,show=False) # show = True to display intermediate results
	print(all_sents, exts, ctime, etime)
	print(augument_extractions(exts))
	if len(exts) == 0:
		print('zero_extraction')
	# break
	# ctags = predict_with_model(model,s,tokenizer)
	print('------------------------------------------------------------------------------------------------------------------\n------------------------------------------------------------------------------------------------------------------\n')
ttaken = round(time.time() - start_time, 3)
print(ttaken)
# input('Press Enter')
exit()
# ------------------------------------------------------------


# -------------- This is for hindi-benchie extraction --------------
def aavg(l):
	return sum(l)/len(l)

print('hindi benchie ')
nlp = load_stanza_model(lang, use_gpu)

df = pd.DataFrame([],columns=['sentence','all_sents','extractions','augmented_exts','ctime','etime'])
i = 0

file = open('benchie_hindi/sents.txt','r') # path to sents.txt
content = [x.strip().split('\t')[1] for x in file.readlines()]
content2 = content.copy()
file.close()

# _, content2 = resolve_coreferences_for_hindi(content, coref_model, nlp)
assert len(content2) == len(content)

j=0
tm = 0
t = tqdm(zip(content, content2), ncols=100, total=len(content))
avg = 0
for sorig, sent in t:
	# sent = sent.split('\t')[1] # old
	if not foreign_characters(sent) and len(sent.split()) < 514:
		try:
			try:
				all_sents, exts, ctime, etime = perform_extraction(sent,lang,model,tokenizer, nlp,show=False,is_a_override=True)
			except Exception as e:
				# continue
				all_sents, exts, ctime, etime = perform_extraction(sent,lang,model,tokenizer, nlp,show=True,is_a_override=True)
			df.at[i,'sentence'] = sorig # sent
			df.at[i,'all_sents'] = all_sents
			df.at[i,'extractions'] = exts
			df.at[i,'augmented_exts'] = augument_extractions(exts)
			df.at[i,'ctime'] = ctime
			df.at[i,'etime'] = etime
			i+=1
		except Exception as e:
			raise "Error"
			print('\n'+str(j+1)+' Error came at')
			print(sent)
			print(e)
			j+=1
			#exts, ctime, etime = perform_extraction(sent,lang,model,tokenizer, nlp,show=True)
		
		tm+=(aavg(ctime)+aavg(etime))
		avg = tm/(i+j)
		t.set_description('avg '+str(round(avg,3))+'s #e '+str(len(df)))
		# if i >= 3:
		#     break
		# display(df)
		# input('wait')
	else:
		raise "Error"
		df.at[i,'sentence'] = sent
		df.at[i,'all_sents'] = [sent]
		df.at[i,'extractions'] = []
		df.at[i,'augmented_exts'] = []
		df.at[i,'ctime'] = []
		df.at[i,'etime'] = []
		i+=1

df.to_hdf('benchie_indie.h5', key=lang, mode='a')
