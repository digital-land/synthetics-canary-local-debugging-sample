import json
_har_header_script = """
function overrideHarHeader(){
    var div = document.createElement('div');
    div.setAttribute("class", "awsDiv");
    div.id = 'headerUI';
    var text = ['Requests','Status code','Response size','Duration'];
    var table = document.createElement('table');
    table.setAttribute("class", "awsTable awsui-table-column-sortable");
    var thead = document.createElement('thead');
    var tr = document.createElement('tr');
    
    for(var i = 0; i < text.length; i++) {
        var th = document.createElement('th');
        
        tr.setAttribute("class", "awsTR");
        if(i == 0) {
            th.setAttribute("width", '27%');
            th.setAttribute("class", "awsTh awsui-table-column-sortable-disabled");
        } else if (i == 1) {
            th.setAttribute("width", '11%');
            th.setAttribute("class", "awsTh awsui-table-column-sortable-enabled");
            th.setAttribute("id", "netStatusColHeader");
        } else if (i == 2) {
            th.setAttribute("width", '12%');
            th.setAttribute("class", "awsTh awsui-table-column-sortable-enabled");
            th.setAttribute("id", "netSizeColHeader");
        } else if (i == 3) {
            th.setAttribute("width", '100%');
            th.setAttribute("class", "awsTh awsui-table-column-sortable-enabled");
            th.setAttribute("id", "netTimeColHeader");
        }
        var span = document.createElement('span');
        span.setAttribute("class", "awsSpan awsui-table-header-content");
        var textSpan = document.createElement('span');
        textSpan.appendChild(document.createTextNode(text[i]));
        span.appendChild(textSpan)
        var arrowSpan = document.createElement('span');
        arrowSpan.setAttribute("class", "awsui-table-sorting-icon awsui-icon-size-normal");
        addSortIcon(arrowSpan, false, true);
        arrowSpan.setAttribute("style", "float: right")
        span.appendChild(arrowSpan);

        th.appendChild(span);
        tr.appendChild(th);
    }
    thead.appendChild(tr);
    table.appendChild(thead);
    div.appendChild(table);
    document.body.appendChild(div);
}
overrideHarHeader();

window.addEventListener('load', setClickEvents);

var clickEventsWaitThreshold = 5;
function setClickEvents() {
    var labelRows = document.getElementsByClassName('pageRow');
    if(labelRows.length == 0 && clickEventsWaitThreshold > 0) {
        setTimeout(setClickEvents, 300);
        clickEventsWaitThreshold--;
        return;
    }
    for(var index = 0; index < labelRows.length; index++) {
        labelRows[index].addEventListener('click', removePreviousSort);
        labelRows[index].addEventListener('click', addStatusSvg);
    }
    addStatusSvg();
}

var addStatusWaitThreshold= 5;
function addStatusSvg() {
    var netStatuses = document.getElementsByClassName("netStatusLabel");
    if(netStatuses.length == 0 && addStatusWaitThreshold > 0) {
        setTimeout(addStatusSvg, 300);
        addStatusWaitThreshold--;
        return;
    }
    if (netStatuses == null || netStatuses.length == 0) {
        addStatusWaitThreshold = 5;
        return;
    }

    const failed = createIcon(false);
    const success = createIcon(true);

    for (var index = 0; index < netStatuses.length; index++) {
        if (netStatuses[index].innerHTML.localeCompare("400") < 0) {    
            netStatuses[index].parentElement.insertBefore(success.cloneNode(true), netStatuses[index]);

        }
        else {
            netStatuses[index].parentElement.insertBefore(failed.cloneNode(true), netStatuses[index]);
        }
    }
    
}
function createIcon(isSuccess) {
    var iconSpan = document.createElement('span');
    iconSpan.setAttribute("class", "awsui-table-status-icon awsui-icon-size-normal");
    if(isSuccess) {
        createSuccessIcon(iconSpan);
    }
    else {
        createFailedIcon(iconSpan);
    }

    return iconSpan;
}

function createFailedIcon(parentSpan) {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 16 16");
    const cir = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    cir.setAttribute('cx', 8);
    cir.setAttribute('cy', 8);
    cir.setAttribute('r', 7);
    cir.setAttribute('stroke', 'red');

    const line1 = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line1.setAttribute('x1', 10.82843);
    line1.setAttribute('y1', 5.17157);
    line1.setAttribute('x2', 5.17157);
    line1.setAttribute('y2', 10.82843);
    line1.setAttribute('style', 'stroke:rgb(255,0,0);stroke-width:2px');

    const line2 = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line2.setAttribute('x1', 10.82843);
    line2.setAttribute('y1', 10.82843);
    line2.setAttribute('x2', 5.17157);
    line2.setAttribute('y2', 5.17157);
    line2.setAttribute('style', 'stroke:rgb(255,0,0);stroke-width:2px');

    svg.appendChild(line1);
    svg.appendChild(line2);
    svg.appendChild(cir);
    parentSpan.appendChild(svg);
}

function createSuccessIcon(parentSpan) {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 16 16");
    const cir = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    cir.setAttribute('cx', 8);
    cir.setAttribute('cy', 8);
    cir.setAttribute('r', 7);
    cir.setAttribute('stroke', '#1d8102');

    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute('d', 'M5 8l2 2 3.521-3.521');
    
    path.setAttribute('style', 'stroke:#1d8102;stroke-width:2px');

    svg.appendChild(path);
    svg.appendChild(cir);
    parentSpan.appendChild(svg);
}
/**Function to sort entries in har file by Http status code/ Duration/ Response size **/
function sortMain(sortBy){

    //ascertain there is data in the table
    if(document.getElementsByClassName('netTable') == undefined || document.getElementsByClassName('netTable').length == 0){
        return;
    }

    //Determine the direction
    var isAsc = determineDirection(sortBy);

    var allTablesToBeSorted = document.getElementsByClassName('netTable');

    for(var i=0; i < allTablesToBeSorted.length; i++) {
            //The table that houses the individual request rows
        var table = document.getElementsByClassName('netTable')[i].children[0];    

        //Each row to be sorted
        var rows = table.getElementsByClassName('netRow');

        //The actual sort
        sortRows(rows, sortBy.id, isAsc);
    }    sortBy.classList.add("awsui-table-column-sorted");

    //Store the fact that we have sorted by this column
    if(isAsc){
        sortBy.setAttribute("data-isasc", true);
    }
}

/** Captures the click event on Status code column **/
document.getElementById("netStatusColHeader").onclick = function(){
    sortMain(this);
}

/** Captures the click event on Response size column **/
document.getElementById("netSizeColHeader").onclick = function(){
    sortMain(this);
}

/** Captures the click event on Duration column **/
document.getElementById("netTimeColHeader").onclick = function(){
    sortMain(this);
}

/** Function to determine if the sort is to be ascending or descending. This also takes care of adding the solid arrow to current header and removing the solid arrow if present else where **/
function determineDirection(header){
    //Check for the isAsc data being set. It is absent if the table isnt sorted by this column or if table is sorted in descending order
    if(!header.dataset.isasc){
        removePreviousSort();
        addNewSort(header, true);
        return true;
    }
    else{
        removePreviousSort();
        addNewSort(header, false);
        return false;
    }
}

function addNewSort(header, isAsc){
    header.classList.add('awsui-table-column-sorted');
    var headerContent = header.getElementsByClassName('awsui-table-header-content')[0].getElementsByClassName('awsui-table-sorting-icon')[0];
    addSortIcon(headerContent, isAsc, false);
}

function addSortIcon(header, isAsc, isEmpty){
    if(header.children[0]){
        header.removeChild(header.children[0]);
    }

    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 16 16");

    // create a triangle
    const triangle = document.createElementNS("http://www.w3.org/2000/svg", "path");

    if(isAsc){
        //triangle pointing downwards
        triangle.setAttribute("d","M4 11h8L8 5l-4 6z");
    }
    else{
        //triangle pointing upwards
        triangle.setAttribute("d", "M4 5h8l-4 6-4-6z");
    }

    if(!isEmpty){
        triangle.setAttribute("class", "filled");
    }

    // attach it to the container
    svg.appendChild(triangle); 
    header.appendChild(svg);
}
/** Function to remove the data for isAsc from all headers, we add this back on later. It also manages the arrow type to be displayed**/ 
function removePreviousSort(){
    var headers = document.getElementsByClassName("awsui-table-column-sortable-enabled");
    for(j = 0; j <= headers.length-1; j++){
        if(headers[j].dataset.isasc){
            headers[j].removeAttribute('data-isasc');
        }
        headers[j].classList.remove("awsui-table-column-sorted");
        addSortIcon(headers[j].getElementsByClassName("awsui-table-header-content")[0].getElementsByClassName("awsui-table-sorting-icon")[0], false, true);
    }
}

/** This is an implementation of bubble sort**/
function sortRows(rows, sortBy, isAsc){
    var swap = true;
    //The last row is summary, hence a check to see if there is only one row
    if(rows.length <= 2){
        return;
    }

    var parent = rows[0].parentNode;
    //Keep the sizer row, which takes care of row width formating intact
    var formatRow = parent.getElementsByClassName("netSizerRow")[0];
    var summaryRow = parent.getElementsByClassName("netSummaryRow")[0];
    var arrRows = Array.from(rows);
    arrRows = arrRows.slice(0, arrRows.length-1);
    arrRows.sort(comparer(sortBy));
    if(!isAsc){
        arrRows.reverse();
    }
    parent.innerHTML = "";
    parent.append(formatRow);
    
    for(i=0; i< arrRows.length; i++){
        parent.append(arrRows[i]);
    }

    parent.append(summaryRow);
}

/** Compare function to compare row values
**/
function comparer(sortBy) { 
      return function(row1, row2) {
          var valA = processCellValue(sortBy, row1), valB = processCellValue(sortBy, row2);
            return !isNaN(valA) && !isNaN(valB) ? valA - valB : valA.toString().localeCompare(valB);
        }
}


/** Retrieve cell value based on type of column
**/
function processCellValue(sortBy, cellVal){
    switch(sortBy){
        case "netStatusColHeader": 
            if(cellVal.getElementsByClassName('netStatusCol')[0].children[1] == undefined) {
                return cellVal.getElementsByClassName('netStatusCol')[0].children[0].innerHTML;
            }
            return cellVal.getElementsByClassName('netStatusCol')[0].children[1].innerHTML;        case "netSizeColHeader": 
            return processResponseSize(cellVal.getElementsByClassName('netSizeCol')[0].children[0].innerHTML);
        case "netTimeColHeader": 
            return processDuration(cellVal.getElementsByClassName('netTimeCol')[0].children[0].getElementsByClassName('netReceivingBar')[0].children[0].innerHTML);
        default:
            return cellVal.getElementsByClassName('netStatusCol')[0].children[0].innerHTML;
    }
}

/** Retrieve cell value if response size is the sorting criteria
**/
function processResponseSize(cellVal){
    var valArr = cellVal.split(" ");
    const dataSizeMap = new Map([
        ["B", 1],
        ["KB", 1000],
        ["MB", 1000000]
    ])
    if(dataSizeMap.has(valArr[1])) {
        return (parseFloat(valArr[0]) * dataSizeMap.get(valArr[1]))
    }
    return cellVal
}

/** Retrieve cell value if process duration is the sorting criteria
**/
function processDuration(cellVal){
    if(!cellVal){
        return cellVal
    }
    const timeMap = new Map([
        ["s", 1000],
        ["min", 60000],
        ["ms", 1],
        ["ns", 0.001]
    ])

    var quantity = parseFloat(cellVal)
    var unit = cellVal.replace(quantity, '').trim()

    if(timeMap.has(unit)){
        return (quantity * timeMap.get(unit))
    }
    return cellVal
}
"""

_har_css_override = ".netBlockingBar{background:#c6dbef!important;}.netResolvingBar{background:#9ECAE1!important;}.netConnectingBar{background:#6BAED6!important;}.netSendingBar{background:#408BC2!important;}.netWaitingBar{background:#1B5D8B!important;}.netReceivingBar{background:#0C2C42!important;}.harBody{font-family:'Amazon Ember', 'Helvetica Neue', Roboto, Arial, sans-serif!important;}.harViewBar > .tab{font-family:'Amazon Ember', 'Helvetica Neue', Roboto, Arial, sans-serif!important;}.toolbar{font-family:'Amazon Ember', 'Helvetica Neue', Roboto, Arial, sans-serif!important;}.infoTip{font-family:'Amazon Ember', 'Helvetica Neue', Roboto, Arial, sans-serif!important;}.popupMenu{font-family:'Amazon Ember', 'Helvetica Neue', Roboto, Arial, sans-serif!important;}.pageTable{font-family:'Amazon Ember', 'Helvetica Neue', Roboto, Arial, sans-serif!important; min-width: 100%!important; }.netTable{font-family:'Amazon Ember', 'Helvetica Neue', Roboto, Arial, sans-serif!important;}.netInfoText{font-family:'Amazon Ember', 'Helvetica Neue', Roboto, Arial, sans-serif!important;}.netInfoParamName{font-family:'Amazon Ember', 'Helvetica Neue', Roboto, Arial, sans-serif!important;font-size:11px!important;text-align:left!important;}.netInfoParamValue{font-size:11px!important;}.netInfoHeadersGroup,.netInfoCookiesGroup{font-family:'Amazon Ember', 'Helvetica Neue', Roboto, Arial, sans-serif!important;}.tabAboutBody{font-family:'Amazon Ember', 'Helvetica Neue', Roboto, Arial, sans-serif!important;}.tabHomeBody{font-family:'Amazon Ember', 'Helvetica Neue', Roboto, Arial, sans-serif!important;}.tabHomeBody{font-family:'Amazon Ember', 'Helvetica Neue', Roboto, Arial, sans-serif!important;}.tabDOMBody{font-family:'Amazon Ember', 'Helvetica Neue', Roboto, Arial, sans-serif!important;}.resultsDefaultContent{font-family:'Amazon Ember', 'Helvetica Neue', Roboto, Arial, sans-serif!important;}.tabSchemaBody{font-family:'Amazon Ember', 'Helvetica Neue', Roboto, Arial, sans-serif!important;}.dp-highlighter{font-family:'Amazon Ember', 'Helvetica Neue', Roboto, Arial, sans-serif!important;}.dp-about table{font-family:'Amazon Ember', 'Helvetica Neue', Roboto, Arial, sans-serif!important;}.dp-about .close{font-family:'Amazon Ember', 'Helvetica Neue', Roboto, Arial, sans-serif!important;}.timeInfoTipBar,.timeInfoTipEventBar{height:10px!important;width:10px!important;}.netHrefCol,.netStatusCol,.netTypeCol,.netDomainCol,.netSizeCol,.netTimeCol{padding:0.1rem 0 0.1rem 0 !important;}.netInfoHeadersGroup,.requestBodyBar{font-size:11px!important;}.netStatusLabel {text-align:left!important; position:relative; float:left; left: 22px} .netSizeLabel{text-align:center!important;;}.awsDiv{border-collapse:separate;color:rgba(22, 25, 31);display:block;font-family:'Amazon Ember', 'Helvetica Neue', Roboto, Arial, sans-serif!important;font-weight:400;height:49px;position:absolute;;width:100%;word-spacing:0px;}.awsTable{background-color:rgba(255, 255, 255);border-bottom-color:rgba(128, 128, 128);border-collapse:separate;border-left-color:rgba(128, 128, 128);border-right-color:rgba(128, 128, 128);border-top-color:rgba(128, 128, 128);color:rgba(84, 91, 100);min-width:100%; border-spacing:0;position:absolute;}.awsTR{height:49px; }.awsTh{text-align:left;border-bottom:1px solid #eaeded; box-sizing:border-box;min-height:4rem;position:relative;background:#fafafa;word-break:keep-all;}.awsSpan{display:block;font-size:12px;position:relative;color:#545b64;font-weight:700;padding-right:0.1rem;padding-left:0.5rem;}.netSizerRow > .netHrefCol{width: 32%!important;}.netCol.netStatusCol{ white-space: normal; }.netSizerRow > .netStatusCol{width:13%!important; white-space: normal;}.netSizerRow > .netSizeCol{width:18%!important;}.netSizerRow > .netTimeCol{width:60%!important;}.previewToolbar{display:none;}.harViewBar.tabBar{display:none;}.tabView {min-width: 100%;} .harViewBodies{top:3rem !important;}.netSummaryRow{display:none !important;} .pageInfoCol{padding:0px 0px 4px 10px !important;background:white !important;}.netWindowLoadBar{display:none !important;}.netContentLoadBar{display:none !important;}.netInfoResponseText{font-size:11px !important;}.sourceEditor{border-color:white;}button[id='appendPreview']{border-color:white;color:white;Visibility:hidden;}td[style='vertical-align:middle;padding-bottom: 1px;']{color:white;Visibility:hidden;}.homeBody, .linkAbout, h3, .example{color:white !important;}input[id='validate']{Visibility:hidden;}.tabViewCol, .netInfoCol{background:white !important;}.popupMenuContent, PostTab, .ParamsTab, .HTMLTab{display:none !important;}a{color:white;}.pageRow, .netRow{height:25px;}textarea{Visibility:hidden;}div.tabHomeBody.tabBody.selected > div > div > table > tbody > tr > td:nth-child(2) {visibility: hidden;}.awsDiv > .awsui-table-column-sortable {color: #545b64; cursor: pointer} .awsDiv > .awsui-table-column-sortable .awsui-table-sorting-icon {display: inline-block;vertical-align: top;width: 1.4rem;height: 1.8rem;padding: 0 0.2rem;box-sizing: border-box; position: relative;    right: 0.5rem;} .awsui-table-sorting-icon svg {pointer-events: none;fill: none;stroke: currentColor;stroke-width: 2px;stroke-linejoin: round;stroke-linecap: round;} .awsui-table-sorting-icon svg .filled {fill: currentColor;}}.awsui-table-header-content{ padding: 1rem;}.awsui-table-column-sortable-enabled .awsui-table-header-content:hover { color: #16191f;} .awsui-table-column-sortable-disabled .awsui-table-sorting-icon { visibility: hidden;} .awsui-table-column-sortable-enabled.awsui-table-column-sorted .awsui-table-header-content { color: #16191f; } .awsDiv thead>tr>*:not(:first-child):before {content:''; position: absolute;left: 0;bottom: 25%;height: 50%;border-left: 1px solid #eaeded; -webkit-box-sizing: border-box;box-sizing: border-box;} .awsui-table-status-icon { width: 1.6rem;height: 1.6rem; display: inline-block; fill: none; position: relative; left: 20px; float: left; border-collapse:separate; caption-side:top; color:rgb(29, 129, 2); cursor:auto; direction:ltr; display:inline; empty-cells:show; fill:none; font-family:'Amazon Ember', 'Helvetica Neue', Roboto, Arial, sans-serif; font-size:14px; font-stretch:100%; font-style:normal; font-variant-caps:normal; font-variant-east-asian:normal; font-variant-ligatures:normal; font-variant-numeric:normal; font-weight:400; height:16px; hyphens:manual; letter-spacing:normal; line-height:20px; list-style-image:none; list-style-position:outside; list-style-type:disc; orphans:2; overflow-wrap:normal; overflow-x:hidden; overflow-y:hidden; pointer-events:none; stroke-width:2px; tab-size:8; text-align:start; text-align-last:auto; text-indent:0px; text-shadow:none; text-size-adjust:auto; text-transform:none; visibility:visible; white-space:normal; widows:2; width:16px; word-spacing:0px; -webkit-border-horizontal-spacing:0px; -webkit-border-vertical-spacing:0px; -webkit-box-direction:normal; }"

_har_css_override_script = "var style = document.createElement('style');\n" \
                           + "style.innerHTML = \"" + _har_css_override + "\";\n" \
                           + "document.head.appendChild(style);\n"

_har_cloudfront_dns_by_region = {
    # North America
    "us-east-1": "d36mk6d4qp08yy.cloudfront.net",
    "us-east-2": "d376cc7nbvddr5.cloudfront.net",
    "us-west-1": "d1boz237fnc8ni.cloudfront.net",
    "us-west-2": "d36mk6d4qp08yy.cloudfront.net",
    "ca-central-1": "d1bgzf6modne37.cloudfront.net",
    "ca-west-1": "d1ys0xk6kkmwno.cloudfront.net",

    # Europe
    "eu-north-1": "dl36207xjihi6.cloudfront.net",
    "eu-west-1": "d17g9w6334qwbi.cloudfront.net",
    "eu-west-2": "d1xbt1srav8x3k.cloudfront.net",
    "eu-west-3": "dvy300hyf1040.cloudfront.net",
    "eu-central-1": "d3vkexsi59qijz.cloudfront.net",
    "eu-central-2": "d1ej1u6yrr1cic.cloudfront.net",
    "eu-south-1": "d38qkyphas6ikv.cloudfront.net",
    "eu-south-2": "d1fpys5upg5gd6.cloudfront.net",

    # Asia Pacific
    "ap-northeast-1": "dgcqxl9z8cf9k.cloudfront.net",
    "ap-northeast-2": "dc8s4ui19cvi3.cloudfront.net",
    "ap-northeast-3": "d3spcjcynyry4n.cloudfront.net",
    "ap-southeast-1": "d1o3t5o8thhpk4.cloudfront.net",
    "ap-southeast-2": "d3alwmab56kbbs.cloudfront.net",
    "ap-southeast-3": "d229b2f1gusfga.cloudfront.net",
    "ap-southeast-4": "dnq673dttjgh3.cloudfront.net",
    "ap-east-1": "d5709r5koj3op.cloudfront.net",
    "ap-south-1": "d2yeufnqlbcs16.cloudfront.net",
    "ap-south-2": "dblz7fwi8iuz4.cloudfront.net",

    # South America
    "sa-east-1": "dnjdg6l984qnm.cloudfront.net",

    # Middle East
    "me-south-1": "d3o1pnkwdcjw3i.cloudfront.net",
    "me-central-1": "d1ovph50b9ke7s.cloudfront.net",
    "il-central-1": "d2u3quqehnhixf.cloudfront.net",

    # Africa
    "af-south-1": "d17a803fpfuep.cloudfront.net",

    # China
    "cn-north-1": "cloudwatch-synthetics-har-cn-north-1.s3.cn-north-1.amazonaws.com.cn/harViewer",
    "cn-northwest-1": "cloudwatch-synthetics-har-cn-northwest-1.s3.cn-northwest-1.amazonaws.com.cn/harViewer",

    # Gov Cloud
    "us-gov-east-1": "cloudwatch-synthetics-har-us-gov-east-1.s3.us-gov-east-1.amazonaws.com/harViewer",
    "us-gov-west-1": "cloudwatch-synthetics-har-us-gov-west-1.s3.us-gov-west-1.amazonaws.com/harViewer",

    # ISO
    "us-iso-east-1": "cloudwatch-synthetics-har-us-iso-east-1.s3.us-iso-east-1.c2s.ic.gov/harViewer",
    "us-isob-east-1": "cloudwatch-synthetics-har-us-isob-east-1.s3.us-isob-east-1.sc2s.sgov.gov/harViewer",
    "us-iso-west-1": "cloudwatch-synthetics-har-us-iso-west-1.s3.us-iso-east-1.c2s.ic.gov/harViewer"
}


def get_html_template(har_contents, region):
    dns = _har_cloudfront_dns_by_region.get(region, _har_cloudfront_dns_by_region.setdefault("us-east-1"))
    har_html_template = "<body><script>var harOutput = " + har_contents + "</script>" \
                        + "<script>" + _har_header_script + "</script>" \
                        + "<script>" + _har_css_override_script + "</script></body>" \
                        + "<script src=\"https://" + dns + "/scripts/harInjector.js\"></script>"
    return har_html_template
