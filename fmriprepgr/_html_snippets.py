html_head = r"""<?xml version="1.0" encoding="utf-8" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta name="generator" content="Docutils 0.12: http://docutils.sourceforge.net/" />
<title></title>
<script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js" integrity="sha384-ChfqqxuZUCnJSK3+MXmPNIyE6ZbWh2IMqE241rYiqJxyMiZ6OW/JmZQ5stwEULTy" crossorigin="anonymous"></script>
<script type="text/javascript">
  var subjs = []
  function updateCounts(){
    var counts = {report:{"-1":0, "1":0, "0":0}}

    subjs.forEach(function(val, idx, arr){
      counts.report[val.report] += 1;
    })

    $("#nrpass").text(counts.report["1"])
    $("#nrfail").text(counts.report["0"])
    $("#nrtodo").text(counts.report["-1"])
  }

  function qc_update(run_id, stage, value) {
    if (stage == 'report') {
      subjs[run_id][stage] = parseInt(value)
      updateCounts();
    }
    else {
      subjs[run_id][stage] = value
    }
  }

  function update_all(stage, value) {
    subjs.forEach( subj => {subj[stage]=value})
  }

  function get_csv(items) {
    // https://stackoverflow.com/questions/44396943/generate-a-csv-file-from-a-javascript-array-of-objects
    let csv = ''

    // Loop the array of objects
    for(let row = 0; row < items.length; row++){
        let keysAmount = Object.keys(items[row]).length
        let keysCounter = 0

        // If this is the first row, generate the headings
        if(row === 0){

           // Loop each property of the object
           for(let key in items[row]){

              // This is to not add a comma at the last cell
              // The '\r\n' adds a new line
              csv += key + (keysCounter+1 < keysAmount ? ',' : '\r\n' )
              keysCounter++
           }
           let keysCounterb = 0
           for(let key in items[row]){
               csv += items[row][key] + (keysCounterb+1 < keysAmount ? ',' : '\r\n' )
               keysCounterb++
           }
        }else{
           for(let key in items[row]){
               csv += items[row][key] + (keysCounter+1 < keysAmount ? ',' : '\r\n' )
               keysCounter++
           }
        }

        keysCounter = 0
    }

    // Once we are done looping, download the .csv by creating a link
    let link = document.createElement('a')
    link.id = 'download-csv'
    link.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(csv));
    link.setAttribute('download', 'thistextissolongitmustabsolutelybeuniqueright');
    document.body.appendChild(link)
    document.querySelector('#download-csv').click()
  }

  function parse_id(idstr) {
    return idstr.split('_')[0].split('-')[1]
  }

  var observer = new IntersectionObserver(function(entries, observer) {
      entries.forEach(entry => {
        eid = parse_id(entry.target.id)
        if (entry['intersectionRatio'] == 1 && subjs[eid]['been_on_screen'] == false) {
          subjs[eid]['been_on_screen'] = true
        }
        else if (entry['intersectionRatio'] == 0 && subjs[eid]['been_on_screen'] == true && subjs[eid]['report'] == -1) {
          subjs[eid]['report'] = 1
          observer.unobserve(entry.target)
          updateCounts();
          radioid = 'inlineRadio' + eid
          document.querySelectorAll('[name=' + radioid + ']')[0].checked = true
        }
        /* Here's where we deal with every intersection */
      });
    }
  , {root:document.querySelector('#scrollArea'), threshold:[0,1]});

 </script>
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">
<style type="text/css">
.sub-report-title {}
.run-title {}

h1 { padding-top: 35px; }
h2 { padding-top: 20px; }
h3 { padding-top: 15px; }

.elem-desc {}
.elem-caption {
    margin-top: 15px
    margin-bottom: 0;
}
.elem-filename {}

div.elem-image {
  width: 100%;
  page-break-before:always;
}

.elem-image object.svg-reportlet {
    width: 100%;
    padding-bottom: 5px;
}
body {
    padding: 65px 10px 10px;
}

.boiler-html {
    font-family: "Bitstream Charter", "Georgia", Times;
    margin: 20px 25px;
    padding: 10px;
    background-color: #F8F9FA;
}

div#boilerplate pre {
    margin: 20px 25px;
    padding: 10px;
    background-color: #F8F9FA;
}

</style>
</head>
<body>"""

html_foot = """<script type="text/javascript">
    function toggle(id) {
        var element = document.getElementById(id);
        if(element.style.display == 'block')
            element.style.display = 'none';
        else
            element.style.display = 'block';
    }

</script>
<script>

updateCounts();
document.querySelectorAll('[id^="id"]').forEach(img => {observer.observe(img)})

</script>
</body>
</html>"""

reviewer_initials = """
 <p> Initials: <input type="text" id="initials_box" oninput="update_all('rater', this.value)"></p>
"""

nav= """<nav class="navbar fixed-top navbar-expand-lg navbar-light bg-light">
        <div class="navbar-header">
           Ratings: <span id="nrpass" class="badge badge-success">0</span> <span id="nrfail" class="badge badge-danger">0</span> <span id="nrtodo" class="badge badge-warning">0</span>
         </div>
         <div class="navbar-text">
           <button type="button" class="btn btn-info btn-sm" id="csv_download" onclick="get_csv(subjs)">Download CSV</button>

         </div>
</div>
</nav>"""


def _generate_html_head(dl_file_name):
    """
    generate an html head block where the name of the downloaded file is set appropriately.
    Parameters
    ----------
    dl_file_name : str

    Returns
    -------
    str
    """
    return html_head.replace('thistextissolongitmustabsolutelybeuniqueright', dl_file_name)
