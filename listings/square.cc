#include <gnuradio/io_signature.h>
#include "square2_ff_impl.h"

namespace gr {
  namespace hnez {
    square2_ff::sptr
    square2_ff::make()
    {
      return gnuradio::get_initial_sptr
        (new square2_ff_impl());
    }

    square2_ff_impl::square2_ff_impl()
      : gr::sync_block("square2_ff",
                       gr::io_signature::make(1, 1, sizeof(float)),
                       gr::io_signature::make(1, 1, sizeof(float)))
    {
    }

    square2_ff_impl::~square2_ff_impl()
    {
    }

    int
    square2_ff_impl::work(int noutput_items,
                          gr_vector_const_void_star &input_items,
                          gr_vector_void_star &output_items)
    {
      const float *in = (const float *) input_items[0];
      float *out = (float *) output_items[0];

      for (int i=0; i<noutput_items; i++) {
        out[i]= in[i] * in[i];
      }

      return noutput_items;
    }
  }
}
