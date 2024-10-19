import numpy as np
import pandas as pd

# This assumes data is organized as an array of three arrays
# [ [ 'group' ], [ 'sub_group' ], [ 'value' ] ]

def make_stacked_bar_plot(data, headers, fig, ax, title, x_label, y_label, colors=None):
  assert(len( data ) == 3)
  ax.grid(zorder=0)

  if not colors:
    colors = [
      "#e41a1c",
      "#377eb8",
      "#4daf4a",
      "#984ea3",
      "#ff7f00",
      "#ffff33",
      "#a65628",
      "#f781bf",
      "#999999",
    ]

  rows = zip( data[0], data[1], data[2] )
  df = pd.DataFrame( rows, columns = headers )

  sub_groups = df[ headers[ 1 ] ].drop_duplicates()
  margin_bottom = np.zeros( len( df[ headers[ 0 ] ].drop_duplicates() ) )

  for num, sub_group in enumerate( sub_groups ):
    values = list( df[ df[ headers[ 1 ] ] == sub_group ].loc[ :, headers[ 2 ] ] )

    df[ df[ headers[1] ] == sub_group ].plot.bar( title = title,
                                                  x = x_label,
                                                  y = y_label,
                                                  ax = ax,
                                                  stacked = True,
                                                  bottom = margin_bottom,
                                                  color = colors[ num ],
                                                  label = sub_group,
                                                  legend = False,
                                                  edgecolor='black',
                                                  zorder=3 )
    margin_bottom += values