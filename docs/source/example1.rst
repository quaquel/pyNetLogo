
Example 1: NetLogo interaction through the pyNetLogo connector
--------------------------------------------------------------

This notebook provides a simple example of interaction between a NetLogo
model and the Python environment, using the Wolf Sheep Predation model
included in the NetLogo example library (Wilensky, 1999).

We start by instantiating a link to NetLogo, loading the model, and
executing the ``setup`` command in NetLogo.

.. code:: python

    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    sns.set_style('white')
    sns.set_context('talk')
    
    import jpype
    import pyNetLogo.pyNetLogo
    
    
    netlogo = pyNetLogo.pyNetLogo.NetLogoLink(gui=True)
    
    netlogo.load_model(r'Wolf Sheep Predation_v6.nlogo')
    netlogo.command('setup')

We can use the ``write_NetLogo_attriblist`` method to pass properties to
agents from a Pandas dataframe – for instance, initial values for given
attributes. This improves performance by simultaneously setting multiple
properties for multiple agents in a single function call.

As an example, we first load data from an Excel file into a dataframe.
Each row corresponds to an agent, with columns for each attribute
(including the ``who`` NetLogo identifier, which is required). In this
case, we set coordinates for the agents using the ``xcor`` and ``ycor``
attributes.

.. code:: python

    agent_xy = pd.read_excel('xy_DataFrame.xlsx')
    agent_xy[['who','xcor','ycor']].head(5)




.. raw:: html

    <div>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>who</th>
          <th>xcor</th>
          <th>ycor</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>0</th>
          <td>0</td>
          <td>-24.000000</td>
          <td>-24.000000</td>
        </tr>
        <tr>
          <th>1</th>
          <td>1</td>
          <td>-23.666667</td>
          <td>-23.666667</td>
        </tr>
        <tr>
          <th>2</th>
          <td>2</td>
          <td>-23.333333</td>
          <td>-23.333333</td>
        </tr>
        <tr>
          <th>3</th>
          <td>3</td>
          <td>-23.000000</td>
          <td>-23.000000</td>
        </tr>
        <tr>
          <th>4</th>
          <td>4</td>
          <td>-22.666667</td>
          <td>-22.666667</td>
        </tr>
      </tbody>
    </table>
    </div>



We can then pass the dataframe to NetLogo, specifying which attributes
and which agent type we want to update:

.. code:: python

    netlogo.write_NetLogo_attriblist(agent_xy[['who','xcor','ycor']], 'a-sheep')

We can check the data exchange by returning data from NetLogo to the
Python workspace, using the report method. In the example below, this
returns arrays for the ``xcor`` and ``ycor`` coordinates of the
``sheep`` agents, sorted by their ``who`` number. These are then plotted
on a conventional scatter plot.

The ``report`` method directly passes a string to the NetLogo instance,
so that the command syntax may need to be adjusted depending on the
NetLogo version. The ``netlogo_version`` property of the link object can
be used to check the current version. By default, the link object will
use the most recent NetLogo version which was found.

.. code:: python

    if netlogo.netlogo_version == '6':
        x = netlogo.report('map [s -> [xcor] of s] sort sheep')
        y = netlogo.report('map [s -> [ycor] of s] sort sheep')
    elif netlogo.netlogo_version == '5':
        x = netlogo.report('map [[xcor] of ?1] sort sheep')
        y = netlogo.report('map [[ycor] of ?1] sort sheep')

.. code:: python

    fig, ax = plt.subplots(1)
    
    ax.scatter(x, y, s=4)
    ax.set_xlabel('xcor')
    ax.set_ylabel('ycor')
    ax.set_aspect('equal')
    fig.set_size_inches(4,4)
    
    plt.show()



.. image:: example1_files/example1_8_0.png


We can then run the model for 100 ticks and update the Python coordinate
arrays for the sheep agents, and return an additional array for each
agent’s energy value. The latter is plotted on a histogram for each
agent type.

.. code:: python

    #We can use either of the following commands to run for 100 ticks:
    
    netlogo.command('repeat 100 [go]')
    #netlogo.repeat_command('go', 100)
    
    if netlogo.netlogo_version == '6':
        x = netlogo.report('map [s -> [xcor] of s] sort sheep')
        y = netlogo.report('map [s -> [ycor] of s] sort sheep')
        energy_sheep = netlogo.report('map [s -> [energy] of s] sort sheep')
    elif netlogo.netlogo_version == '5':
        x = netlogo.report('map [[xcor] of ?1] sort sheep')
        y = netlogo.report('map [[ycor] of ?1] sort sheep')
        energy_sheep = netlogo.report('map [[energy] of ?1] sort sheep')
         
    energy_wolves = netlogo.report('[energy] of wolves') #NetLogo returns these in random order

.. code:: python

    from mpl_toolkits.axes_grid1 import make_axes_locatable
    
    fig, ax = plt.subplots(1, 2)
    
    sc = ax[0].scatter(x, y, s=50, c=energy_sheep, cmap=plt.cm.coolwarm)
    ax[0].set_xlabel('xcor')
    ax[0].set_ylabel('ycor')
    ax[0].set_aspect('equal')
    divider = make_axes_locatable(ax[0])
    cax = divider.append_axes('right', size='5%', pad=0.1)
    cbar = plt.colorbar(sc, cax=cax, orientation='vertical')
    cbar.set_label('Energy of sheep')
    
    sns.distplot(energy_sheep, kde=False, bins=10, ax=ax[1], label='Sheep')
    sns.distplot(energy_wolves, kde=False, bins=10, ax=ax[1], label='Wolves')
    ax[1].set_xlabel('Energy')
    ax[1].set_ylabel('Counts')
    ax[1].legend()
    fig.set_size_inches(14,5)
    
    plt.show()



.. image:: example1_files/example1_11_0.png


The ``repeat_report`` method returns a Pandas dataframe containing
reported values over a given number of ticks, for one or multiple
reporters. This assumes the NetLogo model is run using the default
``go`` convention.

The dataframe is indexed by ticks, with labeled columns for each
reporter. In this case, we track the number of wolf and sheep agents
over 200 ticks; the outcomes are first plotted as a function of time.
The number of wolf agents is then plotted as a function of the number of
sheep agents, to approximate a phase-space plot.

.. code:: python

    counts = netlogo.repeat_report(['count wolves','count sheep'], 200)

.. code:: python

    fig, ax = plt.subplots(1, 2)
    
    counts.plot(x=counts.index, ax=ax[0])
    ax[0].set_xlabel('Ticks')
    ax[0].set_ylabel('Counts')
    ax[1].plot(counts['count wolves'], counts['count sheep'])
    ax[1].set_xlabel('Wolves')
    ax[1].set_ylabel('Sheep')
    fig.set_size_inches(14,5)
    
    plt.show()



.. image:: example1_files/example1_14_0.png


The ``repeat_report`` method can also be used with reporters that return
a NetLogo list; this list is converted to a numpy array. In this case,
we track the energy of the wolf and sheep agents over 5 ticks, and plot
the distribution of the wolves’ energy at the final tick recorded in the
dataframe.

.. code:: python

    energy_df = netlogo.repeat_report(['[energy] of wolves', '[energy] of sheep'], 5)
    
    fig, ax = plt.subplots(1)
    
    sns.distplot(energy_df['[energy] of wolves'].iloc[-1], kde=False, bins=20, ax=ax)
    ax.set_xlabel('Energy')
    ax.set_ylabel('Counts')
    fig.set_size_inches(4,4)
    
    plt.show()



.. image:: example1_files/example1_16_0.png


The ``patch_report`` method can be used to return a dataframe which (for
this example) contains the ``countdown`` attribute of each NetLogo
patch. This dataframe essentially replicates the NetLogo environment,
with column labels corresponding to the xcor patch coordinates, and
indices following the pycor coordinates.

.. code:: python

    countdown_df = netlogo.patch_report('countdown')
    
    fig, ax = plt.subplots(1)
    
    patches = sns.heatmap(countdown_df, xticklabels=5, yticklabels=5, cbar_kws={'label':'countdown'}, ax=ax)
    ax.set_xlabel('pxcor')
    ax.set_ylabel('pycor')
    ax.set_aspect('equal')
    fig.set_size_inches(8,4)
    
    plt.show()



.. image:: example1_files/example1_18_0.png


The dataframes can be manipulated with any of the existing Pandas
functions, for instance by exporting to an Excel file. The ``patch_set``
method provides the inverse functionality to ``patch_report``, and
updates the NetLogo environment from a dataframe.

.. code:: python

    countdown_df.to_excel('countdown.xlsx')
    netlogo.patch_set('countdown', countdown_df.max()-countdown_df)

.. code:: python

    countdown_update_df = netlogo.patch_report('countdown')
    
    fig, ax = plt.subplots(1)
    
    patches = sns.heatmap(countdown_update_df, xticklabels=5, yticklabels=5, cbar_kws={'label':'countdown'}, ax=ax)
    ax.set_xlabel('pxcor')
    ax.set_ylabel('pycor')
    ax.set_aspect('equal')
    fig.set_size_inches(8,4)
    
    plt.show()



.. image:: example1_files/example1_21_0.png


Finally, the ``kill_workspace()`` method shuts down the NetLogo
instance.

.. code:: python

    netlogo.kill_workspace()
