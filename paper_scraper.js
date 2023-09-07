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

/*
 * Downloads a page
 *
 * page: int = page number
 * from: string = from date in yyyy-mm-dd format
 * to: string = to date in yyyy-mm-dd format
 * 
 * Pre: None
 * Post: None
 * Return: JSON = JSON of page API call
 */
async function download_page (page, from, to) {
    // LRT
    // Open the JSON containing what pages to show
    let page = await import_json (`api/search?page=${page}&count=44&dfrom=${from}&dto=${to}&order=desc`);

    page ["items"].forEach (async function (i) {
        // Only download news
        // if (i ["url"].contains ("naujienos")) {
            // Download page
        // }
    });

    return page;
}

/*
 * Downloads all pages in a date range
 *
 * from: string = from date in yyyy-mm-dd format
 * to: string = to date in yyyy-mm-dd format
 * 
 * Pre: None
 * Post: None
 * Return: None
 */
async function download_all (from, to) {
    let i = 1, page = await download_page (i, from, to);

    while (page ["items"].length > 0) {
        page = await download_page (i ++, from, to);
    }
}

// LRT
// fetch ("api/search?page=1&count=44&dfrom=2021-01-01&dto=2021-01-31&order=desc");
