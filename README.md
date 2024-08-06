# Statistical App Generator

![SAG logo](/icon.png)

## Background
Statistical App Generator (SAG) is a Python application which generates a Flask app for a statistical model or equation. In its most basic sense, SAG is a 'wrapper' to run a function through a web app, getting user input and displaying output as  requested by the developer.

The intended use of SAG is for making basic web applications to share statistical models, even when the statistician in question is not savvy in web technology. For this reason, SAG takes a very basic configuration and generates a standard application for running a given function. The output application can then be immediately run and deployed, or its source code can be edited to tweak its behavior freely.

SAG was developed by Elliot Topper at the National Institute of Standards and Technology, 2024.

- To use SAG, first install the binary executable file. This file contains all needed templates and configuration.

## Usage - GUI

- To run SAG, simply run the installed executable (either through command-line or by double clicking its icon)
- A GUI will pop up with inputs for each argument.
    - These arguments are further explained in [Arguments](#arguments).
- During app generation, the GUI will freeze; this is expected. If an error occurs, it will show in a pop-up window.
- When generation has completed, the GUI will produce a popup showing the app's location.
    - Navigate to this directory via file explorer.
- To run the application, run `app.bat` (Windows) / `app.sh` (Mac/Linux) and go to http://localhost:5000.

## Usage - CLI

- To run, the following format must be used:
```
$ sag [math_file] -o [out_dir] -c [config_file]
```
These arguments are further explained in [Arguments](#arguments).
- The newly generated web app will be created in `out_dir`/app. Navigate to this directory.
- Install any packages/libraries used in `math_file`.
- To run the application, run `app` and go to http://localhost:5000.

## Arguments

SAG takes three arguments: `math_file`, `out_dir`, and `config_file`.
- `math_file` - This is a source file written in either [R](https://www.r-project.org/) or [Python](https://www.python.org/). Within this file is a function to be executed when a user submits parameters through the application.

    `math_file` can contain any number of functions and variables, but must contain a function with the name `calc` (unless [otherwise specified](#config)). This function must take input and provide output in a specific form:
    - Input - all parameter names (as defined in your [configuration](#config)) must be present as parameters to tis function. This includes names of all options and files.
        - Parameters marked as optionals must still be present in some form in the calculation function (either unused or with default values).
<a id="output-format"></a>
    - Output - function return must be in the form of a key-value pair (R list or Python dictionary), with keys matching [specified output names](#config).
        - Not all outputs specified must be returned in every case.
        - The function may not print any output (this will make the appllication fail to function)
    
        Depending on chosen output types the vales associated with these keys must be as follows:
        - `table` - must be a key-value pair, where each pair in the data structure is associated with a row in the associated table
        - `data_table` - must be a dataframe (either [R Data Frame](https://www.r-tutor.com/r-introduction/data-frame) or [Pandas DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html)); the dataframe will be output as an HTML table
        - `graph` - must be a dataframe with *at least* the two columns specified present. Only these two columns will be output as a graph
        - `text` - accepts any string value

    - Errors can be returned from the calculation function by using either `stop()` in R or `raise` in Python; output messages will be displayed to the user of the application.
- `out_dir` - The absolute or relative (prepend with `/`) path to an output directory. An `app` folder will be generated inside this directory, containing the new application.
- `config_file` - The path to a JSON configuration file (following the [defined format](#config)). This file is used to specify program inputs, outputs, and general settings.

### Config

The required configuration file follows a strict format to ensure effective app generation. The file must be in JSON file format, with keys defined and nested as follows:

    
- `options` (**array** | *required*) - Defines user input options for the resulting application. Must match input parameters to the calculation function.

    Items are defined as:
    - `name` (**string** | *required*) - A unique name for this input, used for passing values within the application.
    - `description` (**string** | *required*) - The title to be displayed with an input when shown to the user.
    - `optional` (**boolean** | *default = false*) - An optional input does not require user input.
    - `type` (**enum** | *required*) - The type of the desired input; must be one of the following options, which defines further config parameters.
        - **`"text"`** - Defines a text input.

            Parameters:

            - `minlength` (**integer** | *default = 0*) - Defines the minimum length of a text input.
            - `maxlength` (**integer** | *default = None*) - Defines the maximum length of a text input.
            - `pattern` (**string** | *default = None*) - A regular expression (RegEx) string used to validate an input;
        - **`"number"`** - Defines a numeric input.

            Parameters:

            - `min` (**number** | *default = None*) - Defines the minimum value for a text input.
            - `max` (**number** | *default = None*) - Defines the maximum value for a text input.
            - `integer` (**boolean** | *default = false*) - Whether only integer values are allowed.
        - **`"checkbox"`** - Defines a boolean input.
        - **`"select"`** - Defines an enumerable input, with a set of options.

            Parameters:
            
            - `options` (**array** | *required*) - An array of options to be options for this parameter. Each option is defined as an object with a `text` and a `value`.
                - `text` (**string** | *required*) - The title of a selection option to be displayed.
                - `value` (**string** | *required*) - A unique value to equate with a value during calculation.
            - `multiselect` (**boolean** | *default = false*) - If true, more than one option may be selected for the parameter, and passed to the calculation function as an array
        - **`"array"`** - Defines a parameter with more than 1 value of the same type (`text` or `number`).
        
            Parameters:
            
            - `length` (**number or string** | *required*) - Either a fixed length for the array, or the `name` of an integer input.
                - If another element's `name` is used, the array's length will be dynamically updated to match the value of the specified element.
            - `items` (**object** | *required*) - The definition for a single option in this array
                - Defined using `type` aseither `number` or `text`, with additional parameters set as desired.

- `output` (**object** | *required*) - Contains details on output formatting for compilation.

    - `function_name` (**string** | *default = "calc"*) - The name of the calculation function within the `math_file`. If not specified, a function of name "calc" is assumed.
    - `format` (**array** | *required*) - A list of output objects, matching those returned from the calculation function.

        Items are defined as:
        - `name` (**string** | *required*) - A unique name for this output, which refers to a key in the return value of the calculation function.
        - `description` (**string** | *required*) - A title to be used for displaying this output.
        - `type` (**enum** | *required*) - The type of the desired output; must be one of the following options, which defines further parameters. Output of the calculation function must be formatted as specified by this array and the [required formatting for output types](#output-format)

            - **`"graph"`** - Output is translated from a dataframe to a native JavaScript graph, using two specified columns on the X and Y axes.

                Parameters:
                - `x_axis` (**string** | *required*) - Specifies the column of the returned dataframe to plot on the X axis.
                - `y_axis` (**array, "line", "scatter", or "bar"** | *default = "line"*) - Specifies the columns of the returned dataframe to plot on the Y axis.
                
                    If a string is passed, this will be used as the plot type for all columns in the passed dataframe (except `x_axis`).

                    Otherwise, array object must be the following type:
                    - `column_name` (**string** | *required*) - The name of a valid dataframe column to graph.
                    - `plot_type` (**enum** | *default = "line"*) - The plot type to be displayed for this graph. Options are:
                        - **`"line"`**
                        - **`"scatter"`**
                        - **`"bar"`**
                - `x_label` (**string** | *default = `x_axis`*) - A label to display on the graph's X axis.
                - `y_label` (**string** | *required*`) - A label to display on the graph's Y axis.
                - `legend` (**boolean** | *default = true*) - If false, the default legenr for the resulting graph will be disabled.

            - **`"table"`** - Output is translated from a key-value pair to an HTML table element.
            
                Parameters:
                - `precision` (**integer (0-6), array, or "any"** | *default = "any"*) - Defines the precision (number of decimal places) with which to round numbers in the resulting table. If "any" is used, no rounding will occur. If a single integer is used, all numbers will be rounded to `precision` decimal places. If an array is used, the array's length must match the number of output columns, and numbers in each column will be rounded to `precision[i]` decimal places, where i is the column's index.

                    For a `table` output, for an array to be used for `precision` itmust be of length 2.

            - **`"data_table"`** - Output is displayed from a dataframe as an HTML table element.

                Parameters:
                - `precision` (**integer (0-6), array, or "any"** | *default = "any"*) - Defines the precision (number of decimal places) with which to round numbers in the resulting table. If "any" is used, no rounding will occur. If a single integer is used, all numbers will be rounded to `precision` decimal places. If an array is used, the array's length must match the number of output columns, and numbers in each column will be rounded to `precision[i]` decimal places, where i is the column's index.

            - **`"text"`** - Output is displayed to the application as provided in the calculation function.

- `settings` (**object** | *required*) - Contains extra site output settings.

    - `title` (**string** | *required*) - The title of the resulting application.
    - `themeColor` (**enum** | *default = "light*) - A choice of one of the following predefined color themes for the resulting application.
        - **`"light"`**
        - **`"dark"`**
        - **`"blue"`**
        - **`"red"`**
        - **`"green"`**
    - `input_file` (**object**) - Contains setting related to file inputs, which are handled separately from normal options.
        - `graph_input` (**boolean** | *default = true*) - If *true*, file inputs will be graphed in a scatterplot when uploaded by the user to show data.
        - `files` (**array** | *default = []) - A list of CSV file definitions for upload in the application. These are uploaded to the calculation function as dataframes.

            Items are defined as:
            - `name` (**string** | *required*) - A unique name for this file input, whch is displayed the the user and used as a parameter in the calculation function.
            - `optional` (**boolean** | *default = false*) - If false, the file must be included in the user's request; otherwise, this file is optional.
            - `x_param` (**string** | *default = "x"*) - The column of the uploaded CSV file to be read as the x-axis for graphing.
            - `y_param` (**string** | *default = "y"*) - The column of the uploaded CSV file to be read as the y-axis for graphing.