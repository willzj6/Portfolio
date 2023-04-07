import json, re
# Quick and dirty script to create a UHD_Graphics.json for matching the correct processor to UHD Graphics series.
# Data taken from: https://ark.intel.com/content/www/us/en/ark.html#@PanelLabel211968

uhdP630All = '''
Intel® Xeon® W-1250 Processor
Launched
Intel® Xeon® W-1250P Processor
Launched
Intel® Xeon® W-1270 Processor
Launched
Intel® Xeon® W-1270P Processor
Launched
Intel® Xeon® W-1290 Processor
Launched
Intel® Xeon® W-1290P Processor
Launched
Intel® Xeon® W-1290T Processor
Launched
Intel® Xeon® E-2254ME Processor
Launched
Intel® Xeon® E-2254ML Processor
Launched
Intel® Xeon® E-2276ME Processor
Launched
Intel® Xeon® E-2276ML Processor
Launched
Intel® Xeon® E-2224G Processor
Launched
Intel® Xeon® E-2226G Processor
Launched
Intel® Xeon® E-2244G Processor
Launched
Intel® Xeon® E-2246G Processor
Launched
Intel® Xeon® E-2274G Processor
Launched
Intel® Xeon® E-2276G Processor
Launched
Intel® Xeon® E-2276M Processor
Launched
Intel® Xeon® E-2278G Processor
Launched
Intel® Xeon® E-2286G Processor
Launched
Intel® Xeon® E-2286M Processor
Launched
Intel® Xeon® E-2288G Processor
Launched
Intel® Xeon® E-2124G Processor
Launched
Intel® Xeon® E-2126G Processor
Launched
Intel® Xeon® E-2144G Processor
Launched
Intel® Xeon® E-2146G Processor
Launched
Intel® Xeon® E-2174G Processor
Launched
Intel® Xeon® E-2176G Processor
Launched
Intel® Xeon® E-2186G Processor
Launched
Intel® Xeon® E-2176M Processor
Launched
Intel® Xeon® E-2186M Processor
Launched'''

uhd630Embedded = '''Intel® Xeon® W-1250E Processor
Launched
Intel® Xeon® W-1250TE Processor
Launched
Intel® Xeon® W-1270E Processor
Launched
Intel® Xeon® W-1270TE Processor
Launched
Intel® Xeon® W-1290E Processor
Launched
Intel® Xeon® W-1290TE Processor
Launched
Intel® Core™ i3-10100E Processor
Launched
Intel® Core™ i3-10100TE Processor
Launched
Intel® Core™ i5-10500E Processor
Launched
Intel® Core™ i5-10500TE Processor
Launched
Intel® Core™ i7-10700E Processor
Launched
Intel® Core™ i7-10700TE Processor
Launched
Intel® Core™ i9-10900E Processor
Launched
Intel® Core™ i9-10900TE Processor
Launched
Intel® Core™ i3-9100E Processor
Launched
Intel® Core™ i3-9100HL Processor
Launched
Intel® Core™ i3-9100TE Processor
Launched
Intel® Core™ i5-9500E Processor
Launched
Intel® Core™ i5-9500TE Processor
Launched
Intel® Core™ i7-9700E Processor
Launched
Intel® Core™ i7-9700TE Processor
Launched
Intel® Core™ i7-9850HE Processor
Launched
Intel® Core™ i7-9850HL Processor
Launched
Intel® Xeon® E-2226GE Processor
Launched
Intel® Xeon® E-2278GE Processor
Launched
Intel® Xeon® E-2278GEL Processor
Launched
Intel® Core™ i3-8100H Processor
Launched
Intel® Core™ i3-8100T Processor
Launched
Intel® Core™ i5-8400H Processor
Launched
Intel® Core™ i5-8500 Processor
Launched
Intel® Core™ i5-8500T Processor
Launched
Intel® Core™ i7-8700T Processor
Launched
Intel® Core™ i7-8850H Processor
Launched
Intel® Core™ i3-8100 Processor
Launched
Intel® Core™ i7-8700 Processor
Launched'''

uhd630Mobile = '''Intel® Core™ i5-9300H Processor
Launched
Intel® Core™ i5-9400H Processor
Launched
Intel® Core™ i7-9750H Processor
Discontinued
Intel® Core™ i7-9850H Processor
Launched
Intel® Core™ i9-9880H Processor
Launched
Intel® Core™ i9-9980HK Processor
Launched
Intel® Core™ i3-8100B Processor
Discontinued
Intel® Core™ i3-8100H Processor
Launched
Intel® Core™ i5-8300H Processor
Launched
Intel® Core™ i5-8400B Processor
Discontinued
Intel® Core™ i5-8400H Processor
Launched
Intel® Core™ i5-8500B Processor
Discontinued
Intel® Core™ i7-8700B Processor
Launched
Intel® Core™ i7-8750H Processor
Launched
Intel® Core™ i7-8850H Processor
Launched
Intel® Core™ i9-8950HK Processor
Launched'''

uhd620Embedded = '''Intel® Core™ i3-8145UE Processor
Launched
Intel® Core™ i5-8365UE Processor
Launched
Intel® Core™ i7-8665UE Processor
Launched'''

uhd620Mobile = '''Intel® Core™ i3-8140U Processor
Discontinued
Intel® Core™ i5-8260U Processor
Launched
Intel® Core™ i3-8130U Processor
Discontinued
Intel® Core™ i5-8250U Processor
Launched
Intel® Core™ i5-8350U Processor
Launched
Intel® Core™ i7-8550U Processor
Launched
Intel® Core™ i7-8650U Processor
Launched'''

uhd617Mobile = '''Intel® Core™ i5-8310Y Processor
Launched
Intel® Core™ i5-8210Y Processor
Discontinued'''

uhd615Mobile = '''Intel® Core™ i3-10100Y Processor
Launched
Intel® Pentium® Gold 6500Y Processor
Launched
Intel® Pentium® Gold Processor 4425Y
Launched
Intel® Core™ i5-8200Y Processor
Launched
Intel® Core™ i7-8500Y Processor
Launched
Intel® Core™ m3-8100Y Processor
Launched'''

uhd610Embedded = '''Intel® Celeron® Processor G5900E
Launched
Intel® Celeron® Processor G5900TE
Launched
Intel® Pentium® Gold G6400E Processor
Launched
Intel® Pentium® Gold G6400TE Processor
Launched
Intel® Celeron® Processor 4305UE
Launched
Intel® Celeron® Processor G4930E
Launched
Intel® Celeron® Processor G4932E
Launched
Intel® Celeron® G4900 Processor
Launched
Intel® Celeron® G4900T Processor
Launched
Intel® Pentium® Gold G5400 Processor
Launched
Intel® Pentium® Gold G5400T Processor
Launched'''

uhd605Mobile = '''Intel® Pentium® Silver J5040 Processor
Launched
Intel® Pentium® Silver N5030 Processor
Launched
Intel® Pentium® Silver J5005 Processor
Discontinued
Intel® Pentium® Silver N5000 Processor
Discontinued'''

uhd600Mobile = '''Intel® Celeron® Processor J4025
Launched
Intel® Celeron® Processor J4125
Launched
Intel® Celeron® Processor N4020
Launched
Intel® Celeron® Processor N4120
Launched
Intel® Celeron® J4005 Processor
Discontinued
Intel® Celeron® J4105 Processor
Discontinued
Intel® Celeron® Processor N4000
Discontinued
Intel® Celeron® Processor N4100
Discontinued'''

def clean_strings(*strings):
    # Grab the processor models in each string and returns them in list
    # Only for this specific script
    uhdList = []
    for string in strings:
        modelRegex = r'\s(([A-Z][A-Z0-9-]*|i.*)?\d{3,}\w*)'
        for line in re.split(r'\nLaunched|\nDiscontinued', string):
                    model = re.search(modelRegex, line)
                    if model:
                           uhdList += [model.group(0).strip()]

    return uhdList

UHD_Graphics = {}
UHD_Graphics['UHD Graphics P630'] = clean_strings(uhdP630All)
UHD_Graphics['UHD Graphics 630'] = clean_strings(uhd630Embedded, uhd630Mobile)
UHD_Graphics['UHD Graphics 620'] = clean_strings(uhd620Embedded, uhd620Mobile)
UHD_Graphics['UHD Graphics 617'] = clean_strings(uhd617Mobile)
UHD_Graphics['UHD Graphics 615'] = clean_strings(uhd615Mobile)
UHD_Graphics['UHD Graphics 610'] = clean_strings(uhd610Embedded)
UHD_Graphics['UHD Graphics 605'] = clean_strings(uhd605Mobile)
UHD_Graphics['UHD Graphics 600'] = clean_strings(uhd600Mobile)

with open('UHD_Graphics.json', 'w') as f:
       json.dump(UHD_Graphics, f, ensure_ascii=False, indent=4)