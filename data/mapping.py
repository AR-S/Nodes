import json

mapping = {
  'mapping' : [
    {
      'node' : 1,
      'datafile' : 'data/KRX_009540.json'
    },
    {
      'node' : 2,
      'datafile' : 'data/KRX_010140.json'
    },
    {
      'node' : 3,
      'datafile' : 'data/KRX_010620.json'
    },
    {
      'node' : 4,
      'datafile' : 'data/KRX_042660.json'
    },
    {
      'node' : 5,
      'datafile' : 'data/KRX_067250.json',
    },
    {
      'node' : 6,
      'datafile' : 'data/PINK_YSHLF.json',
    },
    # must repeat some from here on
    {
      'node' : 7,
      'datafile' : 'data/KRX_009540.json',
    },
    {
      'node' : 8,
      'datafile' : 'data/KRX_067250.json',
    },
    {
      'node' : 9,
      'datafile' : 'data/KRX_010620.json',
    },
    {
      'node' : 10,
      'datafile' : 'data/PINK_YSHLF.json',
    }
]
}

with open('mapping.json', 'w') as outfile:
    json.dump(mapping, outfile)
