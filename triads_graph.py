# -*- coding: utf-8 -*-
"""
@author: hazenut
@license: MIT

This script generate a graph showing all just intonation triads within
certain complexity limit and range limit
"""

import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba

# -------------------------------------------------------------------------
# Generate all positive integer triads (a,b,c) with a≤b and a≤c, gcd=1, 
# a*b*c≤N, and with x_cent and y_cent <= max_cents. Can be used to generate
# both otonal triads and utonal triads. Utonal triads simply have flipped
# cents relationship.
# Note that permutations of the same triad, i.e. (a,b,c) and (a,c,b) will
# both be generated.
# -------------------------------------------------------------------------
def generate_triads(max_size = 10000, max_cents = 2400):
    a=b=c=1
    while(a<=max_size**(1/3)):
        b=a
        x_cent = 1200.0 * math.log2(b / a)
        
        while(a*b*b<=max_size and x_cent<=max_cents):
            c=a
            y_cent = 1200.0 * math.log2(c / a)
            
            while (a*b*c<=max_size and y_cent<=max_cents):
                if math.gcd(a, math.gcd(b, c)) == 1:
                    weight = 1.0 / (a*b*c)
                    yield (a, b, c, x_cent, y_cent, weight)
                c += 1
                y_cent = 1200.0 * math.log2(c / a)
                
            b+=1
            x_cent = 1200.0 * math.log2(b / a)

        a+=1


# -------------------------------------------------------------------------  
# Return list lpf where lpf[i] = largest prime factor of i (i>=2), lpf[1]=1
# -------------------------------------------------------------------------  
def largest_prime_factor_sieve(limit):
    lpf = list(range(int(limit) + 1))     # initialise with the number itself
    for i in range(2, int(limit)+1):
        if lpf[i] == i:                   # i is prime
            for j in range(2 * i, int(limit) + 1, i):
                lpf[j] = i      # store the largest prime factor found so far
    return lpf


# ---------------------------------------------------------------------- 
# Return categories for the prime limits, useful for plotting the shape
# ----------------------------------------------------------------------
def get_prime_category(prime_limits):
    #includes 1 here for ratio 1/1
    categories = ['1','2','3','5','7','11','13','17','19','>19']
    return np.array([categories.index(str(p)) if p<=19 else len(categories)-1 
                     for p in prime_limits])
        

def main():
    N = 10000         # complexity limit
    max_cents = 2400  # range limit
    
    ## marker scaling control, may help reduce clutters
    gamma=0.5
    scaling=1600
    figsize=(20,15)
    
    # option to show all utonal triads under complexity limit, see below
    all_utonal_mode=False

    # Generate triads
    print(f"Generating triads (0<a≤b, a≤c, a*b*c≤N, gcd(a,b,c)=1) "
          f"within {max_cents} cents range...")
    (a_vals,b_vals,c_vals,x_vals_o,y_vals_o,weights_o) = np.array(list(
            generate_triads(N, max_cents))).T
    
    print(f"Number of triads generated: {len(weights_o)}")
    lpf = largest_prime_factor_sieve(max(max(a_vals), max(b_vals), max(c_vals)))
    prime_limits = np.array([max(lpf[int(a)], lpf[int(b)], lpf[int(c)]) 
                             for a, b, c in zip(a_vals, b_vals, c_vals)])
    
    prime_category = get_prime_category(prime_limits)
    
    # We have two modes for showing utonal triads:
    #  all_utonal_mode=False(default) or True
    #  When false, only triads with abc<N are shown on the graph, additionally,
    #  the so called utonal weights are calculated for these triads (see below)
    #  and these utonal weights are plotted alongside the otonal weight
    #  (original weight) at the same location, using hollow markers.
    #
    #  When true, all triads satisfying lcm(a,b,c)^3/(abc)<N are also shown
    #  on the graph. Evidently, if a triad satisfies abc<N, its mirror flipped
    #  version should satisfy the above and vice versa. These mirror triads are
    #  drawn with hollow markers.
    
    
    if all_utonal_mode:
        # In all_utonal_modes, each otonal triad has an associated utonal triad
        # which is exactly its mirror triad. There is special case for degenerate
        # triads, where a≠b=c, two mirror triads will be plotted: (a,a,c) and 
        # (a,c,a). Here the x and y cents of one of the mirror triad will be
        # recorded, while the other one is just x and y cents flipped, and
        # will be taken care of by the plotting routine
        x_vals_u=np.array([x if x>=y else y-x for x,y in zip(x_vals_o,y_vals_o)])
        y_vals_u=np.array([y if y>x else x-y for x,y in zip(x_vals_o,y_vals_o)])
        weights_u = weights_o
        
    else:
        # For default mode (all_utonal_mode=False):
        # Get associated utonal weight for otonal triad (a,b,c):
        # for otonal triad (a,b,c), its utonal weight is weight of its mirror
        # triad (1/a,1/b,1/c) in simplified form. This is regardless of whether
        # the triad's mirror version is simpler or not.
        # for example, (10,12,15) can be considered 15-limit otonality with
        # otonal weight=1/(10*12*15), and it has mirror inverse (1/10,1/12,1/15)=
        # (4,5,6), so its utonal weight=1/(4*5*6).
        # By plotting both otonal weight and utonal weight we can see if a chord
        # is closer to otonal or utonal and how strongly it is so.
        x_vals_u = x_vals_o
        y_vals_u = y_vals_o
        weights_u = np.array([a*b*c/math.lcm(int(a),int(b),int(c))**3 for a,b,c 
                              in zip(a_vals,b_vals,c_vals)])
    
    
    # Plotting
    categories = ['1','2','3','5','7','11','13','17','19','>19']
    colors = {'1':'oldlace', '2':'#202020', '3':'red', '5':'gold',
              '7':'blue', '11':'green', '13':'violet',
              '17':'deepskyblue', '19':'sienna', '>19':'grey'}
    markers = {'1':'o', '2':'o', '3':'o', '5':'o',
              '7':'o', '11':'s', '13':'s',
              '17':'^', '19':'v', '>19':'_'}
    
    fig, ax = plt.subplots(figsize=figsize)
    
    fig.patch.set_facecolor('#eeeeee')  # figure background
    #ax.set_facecolor('#fafafa')        # plot area
    
    for i,cat in enumerate(categories):
        prime_mask = prime_category==i
        
        alpha = 0.65/(1+(prime_limits[prime_mask]/30)**2)
        
        # plot otonal, use solid markers (facecolor)            
        if cat == categories[-1]:
            ax.scatter(x_vals_o[prime_mask], y_vals_o[prime_mask], c=colors[cat],
                       marker='_', label='>19,ot',
                       s=scaling*weights_o[prime_mask]**gamma, 
                       linewidths=0.5, 
                       alpha=alpha)   
        else:
            ax.scatter(x_vals_o[prime_mask], y_vals_o[prime_mask], c=colors[cat], 
                       marker=markers[cat], label=cat,
                       s=scaling*weights_o[prime_mask]**gamma, 
                       linewidths=0.5,
                       alpha=alpha)

        
        # plot utonal, use hollow markers (edgecolor)  
        if cat == categories[-1]:
            # '|'(vline) marker can only have facecolor, treat it differently
            ax.scatter(x_vals_u[prime_mask], y_vals_u[prime_mask], c=colors[cat],
                       marker='|', label='>19,ut', 
                       s=scaling*weights_u[prime_mask]**gamma, 
                       linewidths=0.5, 
                       alpha=alpha)   
        else:
             edgecolors = [to_rgba(colors[cat], a) for a in alpha]
             ax.scatter(x_vals_u[prime_mask], y_vals_u[prime_mask], c='none', 
                        edgecolors=edgecolors, marker=markers[cat],
                        s=scaling*weights_u[prime_mask]**gamma, linewidths=1)
        
        # handle degenerate utonal triads
        # plot the second mirro triad: simply flip the x and y position
        # if first mirror is on x-axis, this one will be on y-axis, vice versa
        if all_utonal_mode:
            duplicate_utonal_mask=np.logical_and(
                prime_mask,np.logical_or(x_vals_u==0,y_vals_u==0))
            
            if cat == categories[-1]:
                #'|'(vline) marker can only have facecolor, treat it differently
                ax.scatter(y_vals_u[duplicate_utonal_mask], 
                           x_vals_u[duplicate_utonal_mask], 
                           c=colors[cat], marker='|', 
                           s=scaling*weights_u[duplicate_utonal_mask]**gamma,
                           linewidths=0.5, 
                           alpha=alpha)
            else:
                 edgecolors = [to_rgba(colors[cat], a) for a in alpha]
                 ax.scatter(y_vals_u[duplicate_utonal_mask], 
                            x_vals_u[duplicate_utonal_mask], 
                            c='none', edgecolors=edgecolors,
                            marker=markers[cat],
                            s=scaling*weights_u[duplicate_utonal_mask]**gamma, 
                            linewidths=1)
             
    
    if all_utonal_mode:
        ax.set_title(f'All otonal and utonal just triads with complexity n < {N}'
                     f' and cents < {max_cents}',
                     fontsize=16, pad=50, fontname='consolas')
        ax.text(0.5, 1.01, ha='center', va='bottom', 
                transform=ax.transAxes, fontsize=10,
                s=f'otonal triads (solid): n=a·b·c < {N} \n'
                  f'utonal triads (hollow): n=lcm(a·b·c)^3/(a·b·c) < {N} \n'
                  'Size of dot indicates triad\'s weight 1/n', 
                fontname='consolas')
    else:
        ax.set_title(f'All just intonation triads with complexity a·b·c < {N}'
                     f' and cents < {max_cents}\n',
                     fontsize=16, pad=30, fontname='consolas')
        ax.text(0.5, 1.01, ha='center', va='bottom', 
                transform=ax.transAxes, fontsize=10,
                s=f'otonal triads (solid): n=a·b·c < {N}\n'
                  'utonal triads (hollow): n=lcm(a·b·c)^3/(a·b·c)\n'
                  'Size of dot indicates triad\'s weight 1/n', 
                fontname='consolas')
    
    ax.set_xlabel('x (cents) = 1200·log₂(b/a)', fontname='consolas')
    ax.set_ylabel('y (cents) = 1200·log₂(c/a)', fontname='consolas')
    
    y_ticks = x_ticks = np.arange(0, max_cents + 100, 100)
    ax.set_xticks(x_ticks)
    ax.set_yticks(y_ticks)
    ax.grid(alpha=0.3, linewidth=0.8)
    
    ax.set_aspect('equal', adjustable='box')
    
    plt.legend(title='Prime Limits', loc='best', bbox_to_anchor=(1,1), 
               labelspacing=1,    # Vertical space between legend entries
               handletextpad=1.0,   # Space between marker and text
               borderpad=2.0,       # Padding inside legend border
               handlelength=1.0,    # Length of legend handles
               handleheight=1.0,    # Height of legend handles
               shadow=True,
               )
    
    plt.tight_layout()
    #plt.savefig("triads.svg", format="svg", transparent=True)
    plt.show()


if __name__ == "__main__":
     main()