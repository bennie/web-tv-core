<?php
/**
 * CSSTidy - CSS Parser and Optimiser
 *
 * CSS Printing class
 * This class prints CSS data generated by csstidy.
 *
 * This file is part of CSSTidy.
 *
 * CSSTidy is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * CSSTidy is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with CSSTidy; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *
 * @license http://opensource.org/licenses/gpl-license.php GNU Public License
 * @package csstidy
 * @author Florian Schmitz (floele at gmail dot com) 2005-2006
 */
 
/**
 * CSS Printing class
 *
 * This class prints CSS data generated by csstidy.
 *
 * @package csstidy
 * @author Florian Schmitz (floele at gmail dot com) 2005-2006
 * @version 1.0
 */
 
class csstidy_print
{
    /**
     * Saves the input CSS string
     * @var string
     * @access private
     */
    var $input_css = '';

    /**
     * Saves the formatted CSS string
     * @var string
     * @access public
     */
    var $output_css = '';

    /**
     * Saves the formatted CSS string (plain text)
     * @var string
     * @access public
     */
    var $output_css_plain = '';

    /**
     * Constructor
     * @param array $css contains the class csstidy
     * @access private
     * @version 1.0
     */
    function csstidy_print(&$css)
    {
        $this->parser    =& $css;
        $this->css       =& $css->css;
        $this->template  =& $css->template;
        $this->tokens    =& $css->tokens;
        $this->charset   =& $css->charset;
        $this->import    =& $css->import;
        $this->namespace =& $css->namespace;
    }

    /**
     * Resets output_css and output_css_plain (new css code)
     * @access private
     * @version 1.0
     */
    function _reset()
    {
        $this->output_css = '';
        $this->output_css_plain = '';
    }

    /**
     * Returns the CSS code as plain text
     * @return string
     * @access public
     * @version 1.0
     */
    function plain()
    {
        $this->_print(true);
        return $this->output_css_plain;
    }

    /**
     * Returns the formatted CSS code
     * @return string
     * @access public
     * @version 1.0
     */
    function formatted()
    {
        $this->_print(false);
        return $this->output_css;
    }
    
    /**
     * Returns the formatted CSS Code and saves it into $this->output_css and $this->output_css_plain
     * @param bool $plain plain text or not
     * @access private
     * @version 2.0
     */
    function _print($plain = false)
    {
        if ($this->output_css && $this->output_css_plain) {
            return;
        }
        
        $output = '';
        if (!$this->parser->get_cfg('preserve_css')) {
            $this->_convert_raw_css();
        }

        $template =& $this->template;

        if ($plain) {
            $template = array_map('strip_tags', $template);
        }
        
        if ($this->parser->get_cfg('timestamp')) {
            array_unshift($this->tokens, array(COMMENT, ' CSSTidy ' . $this->parser->version . ': ' . date('r') . ' '));
        }
        
        if (!empty($this->charset)) {
            $output .= $template[0].'@charset '.$template[5].$this->charset.$template[6];
        }
        
        if (!empty($this->import)) {
            for ($i = 0, $size = count($this->import); $i < $size; $i ++) {
                $output .= $template[0].'@import '.$template[5].$this->import[$i].$template[6];
            }
        }
        
        if (!empty($this->namespace)) {
            $output .= $template[0].'@namespace '.$template[5].$this->namespace.$template[6];
        }
        
        $output .= $template[13];
        $in_at_out = '';
        $out =& $output;
        
        foreach ($this->tokens as $key => $token)
        {
            switch ($token[0])
            {
                case AT_START:
                    $out .= $template[0].$this->_htmlsp($token[1], $plain).$template[1];
                    $out =& $in_at_out;
                    break;
                
                case SEL_START:
                    if($this->parser->get_cfg('lowercase_s')) $token[1] = strtolower($token[1]);
                    $out .= ($token[1]{0} !== '@') ? $template[2].$this->_htmlsp($token[1], $plain) : $template[0].$this->_htmlsp($token[1], $plain);
                    $out .= $template[3];
                    break;
                    
                case PROPERTY:
                    if($this->parser->get_cfg('case_properties') == 2) $token[1] = strtoupper($token[1]);
                    if($this->parser->get_cfg('case_properties') == 1) $token[1] = strtolower($token[1]);
                    $out .= $template[4] . $this->_htmlsp($token[1], $plain) . ':' . $template[5];
                    break;
                
                case VALUE:
                    $out .= $this->_htmlsp($token[1], $plain);
                    if($this->_seeknocomment($key, 1) == SEL_END && $this->parser->get_cfg('remove_last_;')) {
                        $out .= str_replace(';', '', $template[6]);
                    } else {
                        $out .= $template[6];
                    }
                    break;
                
                case SEL_END:
                    $out .= $template[7];
                    if($this->_seeknocomment($key, 1) != AT_END) $out .= $template[8];
                    break;
                
                case AT_END:
                    $out =& $output;
                    $out .= $template[10] . str_replace("\n", "\n" . $template[10], $in_at_out);
                    $in_at_out = '';
                    $out .= $template[9];
                    break;

                case COMMENT:
                    $out .= $template[11] . '/*' . $this->_htmlsp($token[1], $plain) . '*/' . $template[12];
                    break;
            }
        }

        $output = trim($output);
        
        if (!$plain) {
            $this->output_css = $output;
            $this->_print(true);
        } else {
            $this->output_css_plain = $output;
        }
    }
    
    /**
     * Gets the next token type which is $move away from $key, excluding comments
     * @param integer $key current position
     * @param integer $move move this far
     * @return mixed a token type
     * @access private
     * @version 1.0
     */
    function _seeknocomment($key, $move) {
        $go = ($move > 0) ? 1 : -1;
        for ($i = $key + 1; abs($key-$i)-1 < abs($move); $i += $go) {
            if (!isset($this->tokens[$i])) {
                return;
            }
            if ($this->tokens[$i][0] == COMMENT) {
                $move += 1;
                continue;
            }
            return $this->tokens[$i][0];
        }
    }
    
    /**
     * Converts $this->css array to a raw array ($this->tokens)
     * @access private
     * @version 1.0
     */
    function _convert_raw_css()
    {
        $this->tokens = array();
        ksort($this->css);
        
        foreach ($this->css as $medium => $val)
        {
            if ($this->parser->get_cfg('sort_selectors')) ksort($val);
            if ($medium != DEFAULT_AT) {
                $this->parser->_add_token(AT_START, $medium, true);
            }
            
            foreach ($val as $selector => $vali)
            {
                if ($this->parser->get_cfg('sort_properties')) ksort($vali);
                $this->parser->_add_token(SEL_START, $selector, true);
                
                foreach ($vali as $property => $valj)
                {
                    $this->parser->_add_token(PROPERTY, $property, true);
                    $this->parser->_add_token(VALUE, $valj, true);
                }
                
                $this->parser->_add_token(SEL_END, $selector, true);
            }
            
            if ($medium != DEFAULT_AT) {
                $this->parser->_add_token(AT_END, $medium, true);
            }
        }
    }
    
    /**
     * Same as htmlspecialchars, only that chars are not replaced if $plain !== true. This makes  print_code() cleaner.
     * @param string $string
     * @param bool $plain
     * @return string
     * @see csstidy_print::_print()
     * @access private
     * @version 1.0
     */
    function _htmlsp($string, $plain)
    {
        if (!$plain) {
            return htmlspecialchars($string);
        }
        return $string;
    }
      
    /**
     * Get compression ratio
     * @access public
     * @return float
     * @version 1.2
     */
    function get_ratio()
    {
        if (!$this->output_css_plain) {
            $this->formatted();
        }
        return round((strlen($this->input_css) - strlen($this->output_css_plain)) / strlen($this->input_css), 3) * 100;
    }

    /**
     * Get difference between the old and new code in bytes and prints the code if necessary.
     * @access public
     * @return string
     * @version 1.1
     */
    function get_diff()
    {
        if (!$this->output_css_plain) {
            $this->formatted();
        }
        
        $diff = strlen($this->output_css_plain) - strlen($this->input_css);
        
        if ($diff > 0) {
            return '+' . $diff;
        } elseif ($diff == 0) {
            return '+-' . $diff;
        }
        
        return $diff;
    }

    /**
     * Get the size of either input or output CSS in KB 
     * @param string $loc default is "output"
     * @access public
     * @return integer
     * @version 1.0
     */
    function size($loc = 'output')
    {
        if ($loc == 'output' && !$this->output_css) {
            $this->formatted();
        }
        
        if ($loc == 'input') {
            return (strlen($this->input_css) / 1000);
        } else {
            return (strlen($this->output_css_plain) / 1000);
        }
    }
}
?>
