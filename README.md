# parametric-surfaces
An Extension for hammer to create parametric surfaces using displacements.

## The bezier_drawer_new_version script:
This script lets you draw shapes using bezier curves, and when you are satisfied it creates displacements with the same shape.
When you start the script you start with a blue line with one big blue dot on one end, and a small blue dot on the other. The big blue dot is the first dot of your curve and the displacement will be created on your left hand if you were to walk from the big blue dot to the end of the curve. By selecting one of the points a handle will pop up. You are now able to drag the point or the handle, or you can select the other point. If you click somewhere where isn't a handle or a point you will deselect the curve.

### Extra functionalty
#### Curvepart Tools
* With the add curvepart button you will create a new curvepart at the end of your curve, which is extended in a natural way. The last node will automatically be selected.
* With the remove curvepart button you will remove the latest curvepart in your curve, the end node will be selected if the the last node was selected.
* The Invert curve button is not functional yet but should flip the whole curve, for if you messed up the displacements orientation.

#### Axes
Most of this will later be updated to be done with the scroll buttons.
* Difference: this will be the difference between the minimal x value and the maximal x value, and the same for y.
* Xmin: this will be the minimal x value in your viewport
* Ymin:  this will be the minimal y value in your viewport
After you have written the value in you need to press enter.

#### Compile settings
* height: this will be the height of your total displacement wall
* xamount: this will be the amount of displacements you have along the x direction, which will be along the curve
* yamount: this will be the amount of displacements you have along the y direction, which will be along the height
* displength and dispwidth: these values are of the brushes the displacements are made of, but they do not effect the created curve. Keeping the numbers small is advised.

#### Make VMF:
This button will create your vmf with the current vmf settings, and will name it newmap3.vmf. It will be made in the project folder.
