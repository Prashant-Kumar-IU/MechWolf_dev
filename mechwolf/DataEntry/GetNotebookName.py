def get_notebook_json_name(save_dir=None):
    """
    Gets the current Jupyter notebook name and returns it with .json extension
    
    Args:
        save_dir (str, optional): Directory where JSON file should be saved. 
                                 Defaults to current working directory.
    
    Returns:
        str: The full path to the JSON file
    """
    try:
        import os
        import json
        from notebook import notebookapp
        from IPython import get_ipython
        import requests
        
        # Set the save directory to the current working directory if not provided
        if save_dir is None:
            save_dir = os.getcwd()
        
        # Get the IPython instance
        ipython = get_ipython()
        if ipython is None:
            raise RuntimeError("Not running in a Jupyter notebook")

        # Get the connection file and kernel ID from the IPython instance
        connection_file = ipython.config['IPKernelApp']['connection_file']
        kernel_id = os.path.basename(connection_file).split('-', 1)[1].split('.')[0]

        # Iterate over all running Jupyter notebook servers
        for srv in notebookapp.list_running_servers():
            # Construct the URL to get the sessions from the server
            response = srv['url'] + 'api/sessions'
            token = srv.get('token', '')
            if token:
                response += '?token=' + token
            
            try:
                # Get the list of sessions from the server
                sessions = requests.get(response).json()
                
                # Iterate over the sessions to find the one with the matching kernel ID
                for sess in sessions:
                    if sess['kernel']['id'] == kernel_id:
                        # Get the notebook path and name
                        notebook_path = sess['notebook']['path']
                        notebook_name = os.path.basename(notebook_path)
                        # Replace the .ipynb extension with .json
                        json_name = notebook_name.replace('.ipynb', '.json')
                        print(f"Found active notebook: {notebook_name}, creating JSON: {json_name}")
                        # Return the full path to the JSON file
                        return os.path.join(save_dir, json_name)
            except requests.RequestException as e:
                # Handle errors in getting the notebook server information
                print(f"Error getting notebook server information: {e}")
            except (KeyError, TypeError) as e:
                # Handle errors in parsing the session information
                print(f"Error parsing session information: {e}")
        
        # Raise an error if the active notebook name could not be determined
        raise RuntimeError("Could not determine active notebook name")
        
    except Exception as e:
        # Print any other errors that occur
        print(f"Error getting notebook name: {e}")
        return None