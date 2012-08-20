#include "Cowbells/DetConsBase.h"
#include "Cowbells/SensitiveDetector.h"

#include <TKey.h>
#include <TFile.h>
#include <TDirectoryFile.h>
#include <TGraph.h>
#include <G4VPhysicalVolume.hh>
#include <G4MaterialPropertiesTable.hh>
#include <G4MaterialTable.hh>
#include <G4Material.hh>

// for registering sensitive detectors
#include <G4LogicalVolume.hh>
#include <G4LogicalVolumeStore.hh>
#include <G4SDManager.hh>

#include <vector>

#include <iostream>
using namespace std;

Cowbells::DetConsBase::DetConsBase(std::string properties_filename)
    : m_prop_file(properties_filename)
{
}

Cowbells::DetConsBase::~DetConsBase()
{
}

static G4Material* get_mat(const G4MaterialTable& mattab, std::string matname)
{
    size_t nmat = mattab.size();
    for (size_t imat=0; imat < nmat; ++imat) {
        G4Material* mat = mattab[imat];
        if (mat->GetName() == matname.c_str()) { 
            return mat;
        }
    }
    return 0;
}

static void dump(G4VPhysicalVolume* top, int depth) 
{
    std::string tab(depth,' ');

    cerr << tab << top->GetName() << endl;
    G4LogicalVolume* lv = top->GetLogicalVolume();
    int nchilds = lv->GetNoDaughters();
    for (int ind=0; ind<nchilds; ++ind) {
        dump(lv->GetDaughter(ind), depth+1);
    }
}

G4VPhysicalVolume* Cowbells::DetConsBase::Construct()
{
    G4VPhysicalVolume* world = this->ConstructGeometry();
    this->AddMaterialProperties();
    this->RegisterSensDets();
    dump(world, 0);
    return world;
}

void Cowbells::DetConsBase::AddMaterialProperties()
{
    // Tack on any properties.  

    // This is a vector<G4Material*>
    const G4MaterialTable& mattab = *G4Material::GetMaterialTable();

    // Expect TDirectory hiearchy like
    // properties/MATERIALNAME/PROPERTYNAME where properties are
    // expressed as TGraphs.
    TFile* propfile = TFile::Open(m_prop_file.c_str());

    // FIXME: make the property directory configurable
    const char* prop_dir_name = "properties";
    TDirectory* propdir = dynamic_cast<TDirectory*>(propfile->Get(prop_dir_name));

    TList* lom = propdir->GetListOfKeys();
    int nmats = lom->GetSize();
    for (int imat=0; imat < nmats; ++imat) {
        TKey* mkey = (TKey*)lom->At(imat);
        TDirectoryFile* matdir = dynamic_cast<TDirectoryFile*>(mkey->ReadObj());
        if (!matdir) {
            cerr << "Failed to get directory at " << imat << endl;
            cerr << "Thing is called " << lom->At(imat)->GetName() << endl;
            continue;
        }
        std::string matname = matdir->GetName();
        G4Material* mat = get_mat(mattab, matname);
        if (!mat) {
            cerr << "No G4 material named \"" << matname << "\" found, skipping setting its properties" << endl;
            continue;
        }
        
        G4MaterialPropertiesTable* mpt = new G4MaterialPropertiesTable();
        mat->SetMaterialPropertiesTable(mpt);

        TList* lop = matdir->GetListOfKeys();
        int nlops = lop->GetSize();
        for (int ilop=0; ilop < nlops; ++ilop) {
            TKey* pkey = (TKey*)lop->At(ilop);
            TGraph* prop = dynamic_cast<TGraph*>(pkey->ReadObj());
            std::string propname = prop->GetName();
            int proplen = prop->GetN();
            if (proplen == 1) { // scalar
                double propval = prop->GetY()[0];
                mpt->AddConstProperty(propname.c_str(), propval);
                cerr << "Set " << matname << "/" << propname
                     << "[" << proplen << "] = " << propval << endl;
            }
            else {              // vector
                double* propvals = prop->GetY();
                mpt->AddProperty(propname.c_str(), prop->GetX(), propvals, proplen);
                cerr << "Set " << matname << "/" << propname
                     << "[" << proplen << "] : (" << propvals[0] << " - " << propvals[proplen-1] << ")" << endl;
            }
        } // loop over properties
        
    } // loop over materials

}

void Cowbells::DetConsBase::add_sensdet(std::string lvname,
                                        std::vector<std::string> touchables,
                                        std::string hcname,
                                        std::string sdname)
{
    if (hcname.empty()) {
        hcname = lvname + "HC";
    }

    if (sdname.empty()) {
        sdname = "SensitiveDetector";
    }

    if (sdname != "SensitiveDetector") {
        cerr << "Cowbells::DetConsBase::add_sensdet currently only supports Cowbells::SensitiveDetector" << endl;
        return;
    }

    Cowbells::SensitiveDetector* csd = 
        new Cowbells::SensitiveDetector(sdname.c_str(), hcname.c_str(), touchables);
    m_lvsd[lvname] = csd;
}

void Cowbells::DetConsBase::RegisterSensDets()
{
    LVSDMap_t::iterator it, done = m_lvsd.end();

    for (it = m_lvsd.begin(); it != done; ++it) {
        string lvname = it->first;
        G4VSensitiveDetector* sd = it->second;
        G4SDManager::GetSDMpointer()->AddNewDetector(sd);
        G4LogicalVolume* lv = G4LogicalVolumeStore::GetInstance()->GetVolume(lvname.c_str());
        lv->SetSensitiveDetector(sd);
        cerr << "Registered SD \"" << sd->GetName() << "\" with logical volume \"" << lvname << "\"" << endl;
    }
        
}