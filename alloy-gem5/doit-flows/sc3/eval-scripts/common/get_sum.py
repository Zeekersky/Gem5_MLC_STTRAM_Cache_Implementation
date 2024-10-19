def get_sum(d, key_name, num_cores):
  sum = 0
  for i in xrange(num_cores):
    p = "main_cpu%02d" % i
    if key_name in d[p]:
      sum += d[p][key_name]
  return sum