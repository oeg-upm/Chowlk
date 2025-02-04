// The svg file to edit
const editorDiagram = document.getElementById("editor-diagram");
const editorDiagram2 = document.getElementById("editor-diagram-2");
const editorDiagram3 = document.getElementById("editor-diagram-3");
const editorDiagram4 = document.getElementById("editor-diagram-4");

var editorsDiagram = [editorDiagram, editorDiagram2, editorDiagram3, editorDiagram4];

var getEventSourceDiagram = function(evt)
	{
		var source = evt.srcElement || evt.target;

		// Redirects to foreignObject
		if (source.ownerSVGElement == null)
		{
			var fo = source.parentNode;

			while (fo != null && fo.nodeName != 'foreignObject')
			{
				fo = fo.parentNode;
			}

			if (fo != null)
			{
				source = fo;
			}
		}

		// Redirects to SVG element
		if (source.ownerSVGElement != null)
		{
			source = source.ownerSVGElement;
		}

		return source;
	};

editorsDiagram.forEach((element) => {
  //Mouseover event handler
  //While the mouse is on the box => the mouse pointer change in
  //order to indicate to the user that they can click the box
  element.addEventListener("mouseover", () => {
    element.style.cursor = "pointer";
  });

  //Click event handler
  //If the user click on the box => open editor
  element.addEventListener("click", (e) => {
    var url = "https://embed.diagrams.net/?embed=1&ui=atlas&spin=1&modified=unsavedChanges&proto=json";
    // Create an Iframe
    var iframe = document.createElement('iframe');
    iframe.setAttribute('frameborder', '0');
    // source points to editorDiagram
    var source = getEventSourceDiagram(e);

    console.log(source);

    if ((source.nodeName == "IMG" && source.className == "nanocms-diagram") || (source.nodeName == 'svg' && source.className.baseVal == 'nanocms-diagram')) {

      if (source.drawIoWindow == null || source.drawIoWindow.closed) {

        // Implements protocol for loading and exporting with embedded XML
        var receive = function (evt) {
          if (evt.data.length > 0 && evt.source == source.drawIoWindow) {
            var msg = JSON.parse(evt.data);

            // Received if the editor is ready
            if (msg.event == "init") {
              // Sends the data URI with embedded XML to editor
              if (source.nodeName == 'svg') {
                var data = decodeURIComponent(source.getAttribute('content'));
                source.drawIoWindow.postMessage(JSON.stringify({ action: "load", xml: data }),"*");
              }
              else {
                var data = source.getAttribute('src');

                if (!data.startsWith("data:image")){
                  fetch(data)
                    .then((res) => res.text())
                    .then((text) => {
                      //data = text;
                      let regex = 'content="(.*?)"';
                      data = text.substring(text.search("<svg"));
                      console.log(data);
                      data = data.match(regex);
                      console.log(data);
                      source.drawIoWindow.postMessage(JSON.stringify({ action: "load", xml: text }),"*");
                    })
                    .catch((e) => console.error(e));
                }

                else {
                  source.drawIoWindow.postMessage(JSON.stringify({ action: "load", xml: data }),"*");
                }
              }           
            }
            // Received if the user clicks save
            else if (msg.event == "save") {
              // Sends a request to export the diagram as XML with embedded PNG
              source.drawIoWindow.postMessage(
                JSON.stringify({
                  action: "export",
                  format: "xmlsvg",
                  spinKey: "saving",
                }),
                "*"
              );
            }
            // Received if the export request was processed
            else if (msg.event == "export") {
              
              if (source.nodeName == 'svg') {
                  // Workaround for assigning class after setting outerHTML
                  var wrapper = document.createElement('div');
                  var svg = document.createElement('svg');
                  wrapper.appendChild(svg);
                  svg.outerHTML = decodeURIComponent(escape(atob(msg.data.substring(msg.data.indexOf(',') + 1))));
                  wrapper.firstChild.setAttribute('class', 'nanocms-diagram');

                  // Responsive size
                  var w = parseInt(wrapper.firstChild.getAttribute('width'));
                  var h = parseInt(wrapper.firstChild.getAttribute('height'));

                  wrapper.firstChild.setAttribute('viewBox', '0 0 ' + w + ' ' + h);
                  wrapper.firstChild.setAttribute('style', 'max-height:' + h + 'px;');
                  wrapper.firstChild.removeAttribute('height');

                  // Updates the inline SVG
                  source.outerHTML = wrapper.innerHTML;
                } else {
                  // Updates the data URI of the image
                  source.setAttribute('src', msg.data);
                }
            }

            // Received if the user clicks exit
            if (msg.event == "exit") {
              // Closes the editor
              //window.removeEventListener("message", receive);
              document.body.removeChild(iframe);
              source.drawIoWindow.close();
              source.drawIoWindow = null;
            }
          }
        };

        // Opens the editor
        window.addEventListener("message", receive);
        iframe.setAttribute('src', url);
        document.body.appendChild(iframe);

        iframe.onload = () => {
          source.drawIoWindow = iframe.contentWindow;
        }

      } else {
        // Shows existing editor window
        source.drawIoWindow.focus();
      }
    }
  });
});


