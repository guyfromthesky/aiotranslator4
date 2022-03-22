import language_tool_python

import nltk

class LanguageTool:
	def __init__(self, language = 'en'):
		if language == 'en':
			self.language_tool = language_tool_python.LanguageTool('en-US')
		else:
			self.language_tool = language_tool_python.LanguageTool(language)	
	
	def sentence_split(self, paragraph):
		try:
			sentences = nltk.sent_tokenize(paragraph)
		except Exception as e:
			print("Error while splitting sentence:", e)
			return paragraph

		return sentences

	def correct_list(self, sentence_list):
		#print('sentence_list', sentence_list)
		corrected_sentence_list = []
		for sentence in sentence_list:
			#print('sentence', sentence)
			corrected_sentence_list.append(self.correct(sentence))
		return corrected_sentence_list

	def correct(self, string_to_correct):
		if string_to_correct == '':
			return string_to_correct

		matches = self.language_tool.check(string_to_correct)
		my_mistakes = []
		my_corrections = []
		start_positions = []
		end_positions = []
		
		for rules in matches:
			if len(rules.replacements)>0:
				start_positions.append(rules.offset)
				end_positions.append(rules.errorLength+rules.offset)
				my_mistakes.append(string_to_correct[rules.offset:rules.errorLength+rules.offset])
				my_corrections.append(rules.replacements[0])
		
		#print('string_to_correct', string_to_correct)
		my_new_text = list(string_to_correct)
		
		for m in range(len(start_positions)):
			for i in range(len(string_to_correct)):
				my_new_text[start_positions[m]] = my_corrections[m]
				if (i>start_positions[m] and i<end_positions[m]):
					my_new_text[i]=""

		my_new_text = "".join(my_new_text)
		
		return my_new_text

	def check_list(self, sentence_list):
		#print('sentence_list', sentence_list)
		check_result_list = []
		for sentence in sentence_list:
			#print('sentence', sentence)
			check_result_list.append(self.check(sentence))
		return check_result_list

	def check(self, string_to_check = ''):
		if string_to_check == '':
			return string_to_check

		matches = self.language_tool.check(string_to_check)
		my_mistakes = []
		my_corrections = []
		start_positions = []
		end_positions = []
		
		for rules in matches:
			if len(rules.replacements)>0:
				start_positions.append(rules.offset)
				end_positions.append(rules.errorLength+rules.offset)
				my_mistakes.append(string_to_check[rules.offset:rules.errorLength+rules.offset])
				my_corrections.append(rules.replacements[0])
					
		my_new_text = list(string_to_check)
		
		for m in range(len(start_positions)):
			for i in range(len(string_to_check)):
				my_new_text[start_positions[m]] = my_corrections[m]
				if (i>start_positions[m] and i<end_positions[m]):
					my_new_text[i]=""
		
		mistakes_count = len(my_mistakes)
		
		my_new_text = "".join(my_new_text)
		result = {
			'mistakes_count' : mistakes_count,
			'mistakes': my_mistakes,
			'corrections': my_corrections,
			'start_positions': start_positions,
			'end_positions': end_positions,
			'corrected': my_new_text,
		}	

		return result
