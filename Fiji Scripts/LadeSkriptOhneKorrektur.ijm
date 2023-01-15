/*
 * Macro template to process multiple images in a folder
 */

#@ File    (label = "Image directory", style = "directory") inputI
#@ String  (label = "File extension", value=".tif") suffix
#@ Double (label = "Winkelschritt", value=45.0) winkel
#@ Double (label = "delta x in micrometers", value=0.45) xDim
#@ Double (label = "delta y in micrometers", value=0.45) yDim
#@ Double (label = "delta z in micrometers", value=3.13) zDim
#@ Integer (label = "Resampling Factor >=1", value=2) resampleF

// See also Process_Folder.py for a version of this code
// in the Python scripting language.
setBatchMode(true);

processFolder(inputI, suffix, winkel, xDim, yDim, zDim);

// function to scan folders/subfolders/files to find files with correct suffix
function processFolder(inputI, suffix, winkel, xDim, yDim, zDim) {
	listI = getFileList(inputI);
	listI = Array.sort(listI);

	run("3D Viewer");
	call("ij3d.ImageJ3DViewer.setCoordinateSystem", "false");

	// Step 1 Open The Images
	winkelIndex = 0;
	for (i = 0; i < listI.length; i++) {
		print(listI[i]);
		if(endsWith(listI[i], suffix)){
			processFile(inputI, listI[i], winkelIndex, winkel, xDim, yDim, zDim);
			winkelIndex+=1;
		}
	}
	print("END");
}


function deg2Rad(x){
	return x/180*PI
}

function processFile(input, file, wI, winkel, xDim, yDim, zDim) {
	// Do the processing here by adding your own code.
	// Leave the print statements until things work, then remove them.
	print("Processing: " + input + File.separator + file);
	open(input + File.separator + file);
	run("8-bit");
	imageID = getTitle();
	print(imageID);
	Stack.setXUnit("um");
	run("Properties...", " pixel_width="+xDim+" pixel_height="+yDim+" voxel_depth="+zDim+"");	

	print("W: ", winkel,"    i: ",wI);
    print("Winkel: ", winkel*wI);
	// Interaction with the 3D viewer
	// https://www.brainvoyager.com/bv/doc/UsersGuide/CoordsAndTransforms/SpatialTransformationMatrices.html
	call("ij3d.ImageJ3DViewer.add", imageID, "None", imageID, "0", "true", "true", "true", resampleF, "0");
	if (wI > 0){	    
	    rotX = -winkel*wI;
		rotY = 0;
		rotZ = 0;
		phi = deg2Rad(rotX);
		theta = deg2Rad(rotY);
		psi = deg2Rad(rotZ);
		tX = 0;
		tY = 0;
		tZ = 0;
		imageWidth = getWidth();;
		imageHeight = getHeight();
		imageDepth = nSlices();
		cX = (imageWidth*xDim/2);
		cY = (imageHeight*yDim/2);
		cZ = (imageDepth*zDim/2);

		print("parameters");
	    print("rot X: "+ rotX);
	    print("rot Y: "+ rotY);
	    print("rot Z: "+ rotZ);
	    print("mov X: "+ tX);
	    print("mov Y: "+ tZ);
	    print("mov Z: "+ tZ);
	    print("center X: "+ cX);
	    print("center Y: "+ cY);
	    print("center Z: "+ cZ);
		
		m1 = newArray(cos(psi)*cos(theta), 
						sin(phi)*sin(theta)*cos(psi) - sin(psi)*cos(phi), 
						sin(phi)*sin(psi) + sin(theta)*cos(phi)*cos(psi), 
						-cX*cos(psi)*cos(theta) + cX - cY*(sin(phi)*sin(theta)*cos(psi) - sin(psi)*cos(phi)) - cZ*(sin(phi)*sin(psi) + sin(theta)*cos(phi)*cos(psi)) + tX);
		m2 = newArray(sin(psi)*cos(theta), 
						sin(phi)*sin(psi)*sin(theta) + cos(phi)*cos(psi),
						-sin(phi)*cos(psi) + sin(psi)*sin(theta)*cos(phi),
						-cX*sin(psi)*cos(theta) - cY*(sin(phi)*sin(psi)*sin(theta) + cos(phi)*cos(psi)) + cY - cZ*(-sin(phi)*cos(psi) + sin(psi)*sin(theta)*cos(phi)) + tY);
		m3 = newArray(-sin(theta),
						sin(phi)*cos(theta), 
						cos(phi)*cos(theta), 
						sin(theta)*cX - cY*sin(phi)*cos(theta) - cZ*cos(phi)*cos(theta) + cZ + tZ);
		m4 = newArray(0,0,0,1);
	
		m12 = Array.concat(m1, m2);
		m123 = Array.concat(m12, m3);
		m1234 = Array.concat(m123, m4);
		
		Matrix = String.join(m1234, " ");
		print("MATRIX");
		print(Matrix);
		call("ij3d.ImageJ3DViewer.select", imageID);
	    call("ij3d.ImageJ3DViewer.applyTransform", Matrix);
	    //"1.0 0.0 0.0 movX 0.0 1.0 0.0 movY 0.0 0.0 1.0 movZ 0.0 0.0 0.0 1.0 "
	}
	
}
