import language_tool_python


class language_tool:
	def __init__(self, language = 'en'):
		if language == 'en':
			self.language_tool = language_tool_python.LanguageTool('en-US')


	def check(self, string_to_check = ''):
		if string_to_check == '':
			return

		matches = self.language_tool.check(string_to_check)
		my_mistakes = []
		my_corrections = []
		start_positions = []
		end_positions = []
		
		for rules in matches:
			if len(rules.replacements)>0:
				start_positions.append(rules.offset)
				end_positions.append(rules.errorLength+rules.offset)
				my_mistakes.append(text[rules.offset:rules.errorLength+rules.offset])
				my_corrections.append(rules.replacements[0])
					
		my_new_text = list(string_to_check)
		
		for m in range(len(start_positions)):
			for i in range(len(string_to_check)):
				my_new_text[start_positions[m]] = my_corrections[m]
				if (i>start_positions[m] and i<end_positions[m]):
					my_new_text[i]=""
		status = True
		if len(my_mistakes) > 0:
			status = False

		result = {
			'status' : status,
			'mistakes': my_mistakes,
			'corrections': my_corrections,
			'start_positions': start_positions,
			'end_positions': end_positions,
			'corrected': my_new_text,
		}	

		return result
