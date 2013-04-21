#importing the required libraries
import matplotlib.mlab as mlab
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


if __name__ == '__main__':
    file = open('CSV-files-volume', 'rU')
    csv_sizes = file.read()
    file.close()
    
    distribution = {}
    
    for csv_size in csv_sizes.split():
        if csv_size in distribution:
            distribution[csv_size] = distribution[csv_size] + 1
        else:
            distribution[csv_size] = 1
    
    file = open('CSV-files-distribution', 'w')
    
    file.write("filesize, occurences\n")
    
    for distr in distribution:
        file.write(str(distr) + ', ' + str(distribution[distr]) + "\n")
    
    file.close()
    
    # Read data from a CSV file. Click here to download.
    r = mlab.csv2rec("CSV-files-distribution")
    
    
    
    # Create a figure with size 6 x 6 inches.
    fig = Figure(figsize=(6,6))
    
    # Create a canvas and add the figure to it.
    canvas = FigureCanvas(fig)
    
    # Create a subplot.
    ax = fig.add_subplot(111)
    
    labels = ax.get_xticklabels() 
    for label in labels: 
        label.set_rotation(30)
        
    ax.set_autoscalex_on(False)
    ax.set_autoscaley_on(False)
    ax.set_xlim([10,3500000]) #3399216
    ax.set_ylim([0,3500]) #3258
    ax.set_xscale('log')
    
    # Set the title.
    ax.set_title("",fontsize=14)
    
    # Set the X Axis label.
    ax.set_xlabel("Filesize (kB)",fontsize=12)
    
    # Set the Y Axis label.
    ax.set_ylabel("Number of Files",fontsize=12)
    
    # Display Grid.
    ax.grid(True,linestyle='-',color='0.75')
    
    # Generate the Scatter Plot.
    ax.scatter(r.filesize,r.occurences,s=20,color='tomato');
    
    
    # Save the generated Scatter Plot to a PNG file.
    canvas.print_figure('filesizedistribution.png',dpi=500)
