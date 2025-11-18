use markup5ever_rcdom::{Handle, RcDom};
use pyo3::prelude::*;
#[allow(unused_variables, unused_mut)]
use std::cell::RefCell;
use std::rc::Rc;

fn travel_in_node(node: Handle, useful_marked: Rc<RefCell<Vec<Handle>>>) {
    let binding = Rc::clone(&useful_marked);
    let mut useful_marked_mut = binding.borrow_mut();
    match &node.data {
        markup5ever_rcdom::NodeData::Element { name, .. } => {
            useful_marked_mut.push(node.clone());
            dbg!(name);
        }
        _ => {}
    }
    std::mem::drop(useful_marked_mut);
    for child in node.children.borrow().iter() {
        travel_in_node(Rc::clone(child), useful_marked.clone());
    }
}

#[test]
fn test_travel_in_node() {
    dbg!("some");
    use html5ever::{ParseOpts, parse_document, tendril::TendrilSink};
    let mut file = std::fs::File::open("htmlfile.html").expect("File missing");
    let marked_attributes: Rc<RefCell<Vec<Handle>>> = Rc::new(RefCell::new(vec![]));

    let document = parse_document(
        RcDom::default(),
        ParseOpts {
            ..Default::default()
        },
    )
    .from_utf8()
    .read_from(&mut file)
    .unwrap();
    travel_in_node(document.document, marked_attributes.clone());
}
macro_rules! better_result {
    ($rt: ty,$captured_block: block) => {{
        let normale_result: Result<$rt, Box<dyn std::error::Error>> = $captured_block;
        match normale_result {
            Ok(e) => Ok(e),
            Err(error) => Err(pyo3::exceptions::PyRuntimeError::new_err(format!(
                "{error}"
            ))),
        }
    }};
}
#[pymodule]
mod html_parsing_py {
    use std::{cell::RefCell, rc::Rc};

    use crate::travel_in_node;

    use html5ever::{ParseOpts, parse_document, tendril::TendrilSink};
    use markup5ever_rcdom::{Handle, NodeData, RcDom};
    use pyo3::prelude::*;

    #[pyclass]
    struct HtmlWalker {
        file: std::fs::File,
    }
    #[pymethods]
    impl HtmlWalker {
        #[new]
        fn new(file_path: String) -> PyResult<Self> {
            better_result!(Self, {
                match std::fs::File::open(file_path) {
                    Ok(file) => Ok(Self { file }),
                    Err(e) => Err(Box::new(e)),
                }
            })
        }

        fn find_useful_info(&mut self) -> PyResult<()> {
            let marked_attributes: Rc<RefCell<Vec<Handle>>> = Rc::new(RefCell::new(vec![]));
            better_result!((), {
                let document = parse_document(
                    RcDom::default(),
                    ParseOpts {
                        ..Default::default()
                    },
                )
                .from_utf8()
                .read_from(&mut self.file)
                .unwrap();
                travel_in_node(Rc::clone(&document.document), marked_attributes.clone());
                for node in marked_attributes.borrow_mut().iter_mut() {
                    if let NodeData::Element { attrs, .. } = &node.data {
                        let mut attrs = attrs.borrow_mut();
                        for attribute in attrs.iter_mut() {
                            attribute.value = "somewhere".into();
                        }
                    }
                }
                Ok(())
            })
        }
    }
}
