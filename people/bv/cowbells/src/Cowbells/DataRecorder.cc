#include "Cowbells/DataRecorder.h"

#include "G4SDManager.hh"
#include "G4Event.hh"

#include <iostream>
using namespace std;

Cowbells::DataRecorder::DataRecorder(std::string filename)
    : m_file(0)
    , m_tree(0)
    , m_event(0)
{
    this->set_output_file(filename);
}

Cowbells::DataRecorder::~DataRecorder()
{
    this->close();
}


void Cowbells::DataRecorder::set_output_file(std::string filename)
{
    this->close();
    m_file = TFile::Open(filename.c_str(),"recreate");
    m_tree = new TTree("cowbells","Cowbells Simulation Truth Tree");
    //m_event = new Cowbells::Event();
    TBranch* branch = m_tree->Branch("event","Cowbells::Event",&m_event);
    cerr << "Opened \"" << filename << "\" for writing with branch at 0x" << (void*)branch << endl;
    assert (branch);
}


void Cowbells::DataRecorder::close()
{
    if (!m_file) return;
    cerr << "Closing \"" << m_file->GetName() << endl;
    m_file->cd();
    m_tree->Write();            // redundant?
    m_file->Close();
}


void Cowbells::DataRecorder::fill(const G4Event* event)
{
    cerr << "Filling tree" << endl;
    std::string hcName = "PCHC";    // fixme: make configurable
    int hcID = G4SDManager::GetSDMpointer()->GetCollectionID(hcName);
    Cowbells::HitCollection* hc = 
        static_cast<Cowbells::HitCollection*>(event->GetHCofThisEvent()->GetHC(hcID));

    int nhits = hc->entries();
    for (int ind = 0; ind < nhits; ++ind) {
        GHit* ghit = dynamic_cast<Cowbells::GHit*>(hc->GetHit(ind));
        assert(ghit);
        m_event->hc.push_back(ghit->get());
    }

    m_tree->Fill();
    m_event->clear();

    cerr << "Filled tree with " << nhits << " hits" << endl;
}