/*
 * Imports a file
 *
 * path: string = path to file
 * 
 * Pre: None
 * Post: None
 * Return: response = response of file
 */
async function import_file (path) {
    return await fetch (path)
        .catch((error) => console.log ("File Import Error: " + error));
}

/*
 * Imports a file as a JSON
 *
 * path: string = path to file
 * 
 * Pre: None
 * Post: None
 * Return: JSON = JSON of file
 */
async function import_json (path) {
    return await import_file (path)
        .then ((response) => response.json ())
        .catch((error) => console.log ("JSON Import Error: " + error));
}
