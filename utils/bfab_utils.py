import pandas as pd

def get_dataset(order_number, B):
    bc1s, bc2s, ids, names, tubeids = [], [], [], [], []
    
    results = B.read(endpoint="sample", obj={"containerid": str(order_number)}, max_results=None)
    samples = results.get_first_n_results(None)

    for sample in samples:
        if sample.get('type') in ["Library on Run - Illumina"]:
            ids.append(sample.get('id'))
            tubeids.append(sample.get('tubeid'))
            names.append(sample.get('name'))
            bc1s.append(sample.get('multiplexiddmx', None))
            bc2s.append(sample.get('multiplexid2dmx', None))

    final = pd.DataFrame({
        "Sample ID": ids,
        "Tube ID": tubeids,
        "Name": names,
        "orig Barcode 1": bc1s,
        "orig Barcode 2": bc2s,
        "Barcode 1": bc1s,
        "Barcode 2": bc2s
    })

    cols = ["Sample ID", "Tube ID", "Name", "Barcode 1", "orig Barcode 1", "Barcode 2", "orig Barcode 2"]
    final = final[cols]
    final = final.sort_values(by=['Sample ID'], ascending=True)

    return final



def RC(barcode):
    if str(barcode).lower().startswith("si"):
        return barcode
    if type(barcode) != type(0.123325):
        BC = str(barcode).lower()[::-1].strip()

        associations = {"a":"T",
                        "t":"A",
                        "c":"G",
                        "g":"C"}
        newstring = ""

        for character in BC:
            try:
                newstring += associations[character]
            except:
                continue
        return newstring
    else:
        return barcode

def RS(barcode):
    if str(barcode).lower().startswith("si"):
        return barcode
    if type(barcode) != type(0.1233237435612354347451235):
        BC = str(barcode).lower()[::-1].strip()
        associations = {"a":"A",
                        "t":"T",
                        "c":"C",
                        "g":"G"}
        newstring = ""
        for character in BC:
            try:
                newstring += associations[character]
            except:
                continue
        return newstring
    else:
        return barcode

async def update_bfabric(df, B=None):

    ress = []
    ids = list(df['Sample ID'])

    bc1 = [str(i) if type(i) != type(0.1) else "" for i in list(df['Barcode 1'])]
    bc2 = [str(i) if type(i) != type(0.1) else "" for i in list(df['Barcode 2'])]
    bc1 = [''.join(sentence.split()) for sentence in bc1]
    bc2 = [''.join(sentence.split()) for sentence in bc2]
    n_itr = (len(ids) // 100) + 1

    for itr in range(n_itr):
        print(f"Updating {itr*100} to {(itr+1)*100} samples")
        objs = []
        for i in range(100):
            if i+itr*100 >= len(ids):
                break            
            objs.append(
                {
                 "id":str(ids[i+itr*100]),
                 "multiplexiddmx":str(bc1[i+itr*100]),
                 "multiplexid2dmx":str(bc2[i+itr*100])
                }
            )
            
        res = B.save(endpoint="sample", obj=objs)
        ress += res

        if "errorreport" in str(res[0]):
            raise Exception(f"Error in updating B-Fabric: {res[0]}")

    return ress