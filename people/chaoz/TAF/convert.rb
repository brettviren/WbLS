#!/usr/bin/env ruby -wKU

# desc = 'kaon_105MeV_py90'
desc = 'muon_140-240MeV_py0'
range = (1..1)

range.each do |i|
  ii = sprintf("%03d", i)
  cmd  = %{root -b -q 'convert.C(}
  cmd += %{"../gen/root_files/#{desc}/#{desc}_seed#{ii}.root",}
  cmd += %{"../tree/#{desc}/tree#{ii}.root")'}
  puts cmd
  system(cmd)
end

