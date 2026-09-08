import math, unittest
from orbit_engine import pass_intervals, distance
class PassTests(unittest.TestCase):
 def test_brief_grazing_pass_between_samples(self):
  d=lambda t: math.hypot((t-15000)/1000*7,44.9)
  p=pass_intervals(d,0,60000,45)
  self.assertEqual(len(p),1);self.assertLess(p[0]['durationSeconds'],2)
  self.assertAlmostEqual(p[0]['closestKm'],44.9,places=3)
 def test_minimum_in_first_sample_interval(self):
  p=pass_intervals(lambda t:math.hypot((t-10000)/1000*7,44.9),0,60000,45)
  self.assertEqual(len(p),1)
 def test_radius_and_no_pass(self):
  d=lambda t:math.hypot((t-30000)/1000*7,80)
  self.assertEqual(pass_intervals(d,0,60000,45),[])
  p=pass_intervals(d,0,60000,100)[0]
  self.assertAlmostEqual(p['durationSeconds'],120/7,delta=.5)
 def test_window_clipping_and_constant_distance(self):
  p=pass_intervals(lambda t:20,0,60000,45)
  self.assertEqual(len(p),1);self.assertTrue(p[0]['clippedStart']);self.assertTrue(p[0]['clippedEnd'])
 def test_two_passes(self):
  p=pass_intervals(lambda t:abs(math.sin(t/60000*math.pi))*300,0,120000,45)
  self.assertEqual(len(p),3)
 def test_dateline(self):
  self.assertLess(distance({'lat':0,'lon':179.9},{'lat':0,'lon':-179.9}),23)
if __name__=='__main__':unittest.main()
