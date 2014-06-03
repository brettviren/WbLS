void read_number_of_PMTs(const char* rootfile = "../wcsim.root");
void read_number_of_PMTs(const char* rootfile)
{
  gSystem->Load("libWCSimRoot.so");
  TFile *f2 = new TFile(rootfile);  
  TTree *tree = (TTree*)f2->Get("wcsimGeoT");
  WCSimRootGeom* geom = new WCSimRootGeom();
  TBranch *gb = tree->GetBranch("wcsimrootgeom");
  gb->SetAddress(&geom);
  tree->GetEntry(0);
  Printf("Number of PMTs: %d", geom->GetWCNumPMT());
}
