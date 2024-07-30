import pandas as pd
import bfabric

BB = bfabric.Bfabric()

def get_dataset(order_number, B):

    bc1s = []
    bc2s = []
    ids = []
    names = []
    tubeids = []

    res, all_res = B.read_object(endpoint="sample", obj={"containerid":str(order_number)}, page=1), []

    print(res)

    next_page = 2
    while res is not None and len(res):
        all_res += res
        try:
            res = B.read_object(endpoint="sample", obj={"containerid":str(order_number)}, page=next_page)
        except:
            break
        next_page += 1

    samples = all_res
    print(samples)
    # for i in range(19999999999999999999999999999999999999999999999):
    #     samples = B.read_object(endpoint="sample", obj={"containerid":str(order_number)}, page=str(i))
    #     if type(samples) != type(None):
    #         all_samples += samples
    #     else:
    #         break

    # samples = all_samples

    for sample in samples:
        # if sample.type == "Library - Illumina" or sample.type == "User Library in Pool":
        if sample.type == "Library on Run - Illumina":
            ids.append(sample._id)

            try:
                tubeids.append(sample.tubeid)
            except:
                tubeids.append(None)
            try:
                names.append(sample.name)
            except:
                names.append(None)
            try:
                bc1s.append(sample.multiplexiddmx)
            except:
                bc1s.append(None)
            try:
                bc2s.append(sample.multiplexid2dmx)
            except:
                bc2s.append(None)
        else:
            continue

    final = pd.DataFrame({
        "Sample ID":ids,
        "Tube ID":tubeids,
        "Name":names,
        "Barcode 1":bc1s,
        "Barcode 2":bc2s
    })
    final = final.sort_values(by=['Sample ID'], ascending=True)
    # print(final)

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

def update_bfabric(df, B=None):

    print("STARTING")
    if B is None:
        B = BB

    errors = []
    ress = []
    ids = list(df['Sample ID'])

    print(ids)
    bc1 = [str(i) if type(i) != type(0.1) else "" for i in list(df['Barcode 1'])]
    bc2 = [str(i) if type(i) != type(0.1) else "" for i in list(df['Barcode 2'])]
    # Remove Whitespace #
    bc1 = [''.join(sentence.split()) for sentence in bc1]
    # print(bc1)
    bc2 = [''.join(sentence.split()) for sentence in bc2]
    # print(bc2) 
    n_itr = (len(ids) // 100) + 1

    print(n_itr)

    # for i in range(len(ids)):
    for itr in range(n_itr):
        # print("ITR: " + str(itr) + " of " + str(n_itr))
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
            
            # objs.append({"id":str(ids[i+itr*100]),"barcode1dmx":str(bc1[i+itr*100]),"barcode2dmx":str(bc2[i+itr*100])})

        res = B.save_object(endpoint="sample", obj=objs)
        print(res[0])
        # res = B.save_object(endpoint="sample", obj={"id":"0","barcode1dmx":str(bc1[i]),"barcode2dmx":str(bc2[i])})
        # ress.append(res)
        ress += res
        if "errorreport" in str(res[0]):
            print("Recieved Error Report from Bfabric")
            errors.append(str(ids[i]))

    return (ress, errors)