# app_name: (path_to_app, app_input)

app_dir = "/home/qtt2/cornell-brg/awsteal-new-apps/"

apps = {
         "cilk-cilksort" : (app_dir + "cilk-cilksort/cilk-cilksort", \
                            "-n 200000"),
         "cilk-heat"     : (app_dir + "cilk-heat/cilk-heat", \
                            "-g 1 -nx 256 -ny 64 -nt 1"),
         "cilk-knapsack" : (app_dir + "cilk-knapsack/cilk-knapsack", \
                            "-f " + app_dir + \
                            "cilk-knapsack/inputs/knapsack-small-1.input"),
         "cilk-matmul"   : (app_dir + "cilk-matmul/cilk-matmul", \
                            "100"),

#         "cilk-cilksort" : (app_dir + "cilk-cilksort/cilk-cilksort", \
#                            "-n 6000"),
#         "cilk-heat"     : (app_dir + "cilk-heat/cilk-heat", \
#                            "-g 1 -nx 32 -ny 8 -nt 1"),
#         "cilk-knapsack" : (app_dir + "cilk-knapsack/cilk-knapsack", \
#                            "-f " + app_dir + \
#                            "cilk-knapsack/inputs/knapsack-example1.input"),
#         "cilk-matmul"   : (app_dir + "cilk-matmul/cilk-matmul", \
#                            "30"),
       }
