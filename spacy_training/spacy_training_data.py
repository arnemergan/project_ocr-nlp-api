    def convert_dataturks_to_spacy(self,dataturks_JSON_FilePath):
        try:
            training_data = []
            lines=[]
            with open(dataturks_JSON_FilePath, 'r') as f:
                lines = f.readlines()

            for line in lines:
                parsed_json = (json.loads(line))
                text =  ''.join([i if ord(i) < 128 else ' ' for i in parsed_json["content"].replace('\n','')])
                entities = []
                if parsed_json["annotation"] != None:
                    for annotation in parsed_json["annotation"]:
                        #only a single point in text annotation.
                        point = annotation["points"][0]
                        labels = annotation["label"]
                        # handle both list of labels or a single label.
                        if not isinstance(labels, list):
                            labels = [labels]

                        for label in labels:
                            #dataturks indices are both inclusive [start, end] but spacy is not [start, end)
                            entities.append((point['start'], point['end'] + 1 ,label))
                    training_data.append((text, {"entities" : entities}))
            return training_data
        except Exception as e:
           print("Unable to process " + dataturks_JSON_FilePath + "\n" + "error = " + str(e))
           return None