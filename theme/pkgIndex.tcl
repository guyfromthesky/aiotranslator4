package ifneeded awthemes 10.4.0 \
    [list source [file join $dir awthemes.tcl]]
package ifneeded colorutils 4.8 \
    [list source [file join $dir colorutils.tcl]]
package ifneeded awarc 1.6.1 \
    [list source [file join $dir awarc.tcl]]
package ifneeded ttk::theme::awarc 1.6.1 \
    [list source [file join $dir awarc.tcl]]
package ifneeded awblack 7.8.1 \
    [list source [file join $dir awblack.tcl]]
package ifneeded ttk::theme::awblack 7.8.1 \
    [list source [file join $dir awblack.tcl]]
package ifneeded awbreeze 1.9.1 \
    [list source [file join $dir awbreeze.tcl]]
package ifneeded ttk::theme::awbreeze 1.9.1 \
    [list source [file join $dir awbreeze.tcl]]
package ifneeded awbreezedark 1.0.1 \
    [list source [file join $dir awbreezedark.tcl]]
package ifneeded ttk::theme::awbreezedark 1.0.1 \
    [list source [file join $dir awbreezedark.tcl]]
package ifneeded awclearlooks 1.3.1 \
    [list source [file join $dir awclearlooks.tcl]]
package ifneeded ttk::theme::awclearlooks 1.3.1 \
    [list source [file join $dir awclearlooks.tcl]]
package ifneeded awdark 7.12 \
    [list source [file join $dir awdark.tcl]]
package ifneeded ttk::theme::awdark 7.12 \
    [list source [file join $dir awdark.tcl]]
package ifneeded awlight 7.10 \
    [list source [file join $dir awlight.tcl]]
package ifneeded ttk::theme::awlight 7.10 \
    [list source [file join $dir awlight.tcl]]
package ifneeded awtemplate 1.5.1 \
    [list source [file join $dir awtemplate.tcl]]
package ifneeded ttk::theme::awtemplate 1.5.1 \
    [list source [file join $dir awtemplate.tcl]]
package ifneeded awwinxpblue 7.9.1 \
    [list source [file join $dir awwinxpblue.tcl]]
package ifneeded ttk::theme::awwinxpblue 7.9.1 \
    [list source [file join $dir awwinxpblue.tcl]]

if {![file isdirectory [file join $dir Breeze]]} { return }
if {![package vsatisfies [package provide Tcl] 8.6]} { return }

package ifneeded ttk::theme::Breeze 0.8 \
    [list source [file join $dir breeze.tcl]]
package ifneeded breeze 0.8 \
    [list source [file join $dir breeze.tcl]]

package ifneeded ttk::theme::forest-light 1.0 \
    [list source [file join $dir breeze.tcl]]
package ifneeded forest-light 1.0 \
    [list source [file join $dir breeze.tcl]]

package ifneeded ttk::theme::forest-dark 1.0 \
    [list source [file join $dir breeze.tcl]]
package ifneeded forest-dark 1.0 \
    [list source [file join $dir breeze.tcl]]

set base_theme_dir [file join [pwd] [file dirname [info script]]]

array set base_themes {
  aquativo 0.0.1
  black 0.1
  blue 0.7
  clearlooks 0.1
  elegance 0.1
  itft1 0.14
  keramik 0.6.2
  kroc 0.0.1
  plastik 0.6.2
  radiance 0.1
  smog 0.1.1
  winxpblue 0.6
}

foreach {theme version} [array get base_themes] {
  package ifneeded ttk::theme::$theme $version \
    [list source [file join $base_theme_dir $theme $theme.tcl]]

  package ifneeded $theme $version \
    [list source [file join $base_theme_dir $theme $theme.tcl]]
}