import genie_api.common.rand

def generate(model_class, size, id_type):
  if id_type == 'alpha':
    key_name = genie_api.common.rand.rand_alpha_string(size)
  else:
    key_name = genie_api.common.rand.rand_numeric_string(size)
  while True:
    try:
      model_class.objects.get(pk=key_name)
      if id_type == 'alpha':
        key_name = genie_api.common.rand.rand_alpha_string(size)
      else:
        key_name = genie_api.common.rand.rand_numeric_string(size)
    except:
      break
  return key_name
