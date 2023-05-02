'''
Source: https://discourse.paraview.org/t/how-to-export-paraview-colormap-into-a-format-that-could-be-read-by-matplotlib/2436
'''
def ExportPreset(lutName):
  from paraview import servermanager
  presets = paraview.servermanager.vtkSMTransferFunctionPresets()

  lut = GetColorTransferFunction('Velocity')
  lut.ApplyPreset(lutName)

  import vtk
  helper = vtk.vtkUnsignedCharArray()

  dctf = lut.GetClientSideObject()
  dataRange = dctf.GetRange()

  for i in range(0, 256):
    x = (i/255.0) * (dataRange[1]-dataRange[0]) + dataRange[0]
    helper.SetVoidArray(dctf.MapValue(x), 3, 1)
    r = helper.GetValue(0)
    g = helper.GetValue(1)
    b = helper.GetValue(2)
    #print value, r, g, b
    print('%.3f %.5f %.5f %.5f' % (x, r/255.0, g/255.0, b/255.0))

ExportPreset('Turbo')