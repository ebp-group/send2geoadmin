<!DOCTYPE html>
<html lang="en">
<head>
<link href='http://fonts.googleapis.com/css?family=Duru+Sans' rel='stylesheet' type='text/css'>
<meta charset=utf-8>
<meta name="viewport" content="width=620">
<title>Send your local geodata files to geo.admin.ch</title>
<style>
article { width: 600px; margin: 0 auto }
h1 { text-align: center; } 
a {text-decoration:none} 
p { text-align: center; margin-bottom: 5px;} 
#holder { border: 10px dashed #ccc; width: 300px; min-height: 300px; margin: 20px auto;}
#holder.hover { border: 10px dashed #0c0; }
#holder img { display: block; margin: 10px auto; }
#holder p { margin: 10px; font-size: 14px; }
progress { width: 100%; }
.fail { background: #c00; color: #fff; }
.hidden { display: none !important;}
body { font-family: 'Duru Sans', sans-serif; } 
</style>
<body>
		
<article>
	<a href="https://github.com/ernstbaslerpartner/send2geoadmin"> 
		<img style="position: absolute; top: 0; right: 0; border: 0;"
				 src="https://s3.amazonaws.com/github/ribbons/forkme_right_gray_6d6d6d.png" 
				 alt="Fork me on GitHub"></a>  
      <h1>Send your geodata to <a href="http://map.geo.admin.ch">geo.admin.ch</a></h1>
			<p class="fail">{{ error_message }}</p>
			<p id="description">Drag a file from your desktop on to the
			drop zone below. You'll be redirected
			to <a href="http://map.geo.admin.ch">map.geo.admin.ch</a> and
			your data should show up there.</br>
			This is a proof-of-concept. Currently, only
			KMZ and GeoJSON files are supported.</p>.
  <div id="holder">
  </div> 
  <p id="upload" class="hidden"><label>Drag & drop not supported, but you can still upload via this input field:<br><input type="file"
  name="upload"></label></p>
	<p id="formdata">XHR2's FormData is not supported</p>
	<p id="filereader">File API &amp; FileReader API not supported</p>
	<p id="progress">XHR2's upload progress isn't supported</p>
  <p id="progresstext">Upload progress: <progress id="uploadprogress"
  min="0" max="100" value="0">0</progress></p>
	<p>This service is provided as is. Your files are stored temporarily
	on an Azure server with a random URL, so that it can be piped to the
	<a href="http://map.geo.admin.ch">map.geo.admin.ch</a>. Feedback on
	Github or to <a href="http://twitter.com/ping13">@ping13</a> on
	Twitter.<p>
	<p><a href="http://geo.ebp.ch"><img src="/static/geo_ebp_blog_logo.png"></a><p>
</article>
<script>
var holder = document.getElementById('holder'),
    tests = {
      filereader: typeof FileReader != 'undefined',
      dnd: 'draggable' in document.createElement('span'),
      formdata: !!window.FormData,
      progress: "upload" in new XMLHttpRequest
    }, 
    support = {
      filereader: document.getElementById('filereader'),
      formdata: document.getElementById('formdata'),
      progress: document.getElementById('progress')
    },
    progress = document.getElementById('uploadprogress'),
    fileupload = document.getElementById('upload');


"filereader formdata progress".split(' ').forEach(function (api) {
  if (tests[api] === false) {
    support[api].className = 'fail';
  } else {
    // FFS. I could have done el.hidden = true, but IE doesn't support
    // hidden, so I tried to create a polyfill that would extend the
    // Element.prototype, but then IE10 doesn't even give me access
    // to the Element object. Brilliant.
    support[api].className = 'hidden';
  }
});

function readfiles(files) {
    var formData = tests.formdata ? new FormData() : null;
    for (var i = 0; i < files.length; i++) {
      if (tests.formdata) formData.append('upload', files[i]);
    }

    // now post a new XHR request
    if (tests.formdata) {
      var xhr = new XMLHttpRequest();
      xhr.open('POST', '/upload_kmz');
      xhr.onload = function(evt) {
        progress.value = progress.innerHTML = 100;
				var redirect_url = evt.currentTarget.responseText;
				window.location = redirect_url; 
      };
							
      if (tests.progress) {
        xhr.upload.onprogress = function (event) {
          if (event.lengthComputable) {
            var complete = (event.loaded / event.total * 100 | 0);
            progress.value = progress.innerHTML = complete;
          }
        }
      }
					
			xhr.send(formData);
    }
}

if (tests.dnd) { 
  holder.ondragover = function () { this.className = 'hover'; return false; };
  holder.ondragend = function () { this.className = ''; return false; };
  holder.ondrop = function (e) {
    this.className = '';
    e.preventDefault();
    readfiles(e.dataTransfer.files);
  }
} else {
  fileupload.className = 'hidden';
  fileupload.querySelector('input').onchange = function () {
    readfiles(this.files);
  };
}

</script></body>
</html>
